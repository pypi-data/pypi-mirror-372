use crate::table::{Column, ColumnAlign};
use nom::bytes::complete::{is_not, take_till, take_until};
use nom::error::convert_error;
use nom::error::{ParseError, VerboseError};
use nom::multi::{many0, many1};
use nom::IResult;
use nom::{
    branch::alt,
    bytes::complete::{tag, take_while},
    combinator::{all_consuming, map, opt, value},
    error::context,
    sequence::{delimited, preceded, separated_pair, terminated, tuple},
};

type Res<T, U> = IResult<T, U, VerboseError<T>>;

fn ws<'a, E: ParseError<&'a str>>(i: &'a str) -> IResult<&'a str, (), E> {
    let chars = " \n\t\r";
    value((), take_while(move |c| chars.contains(c)))(i)
}
fn eol<'a, E: ParseError<&'a str>>(i: &'a str) -> IResult<&'a str, (), E> {
    // only unix, mac and windows line end supported for now
    value((), alt((tag("\n\r"), tag("\r\n"), tag("\n"))))(i)
}
fn comment<'a, E: ParseError<&'a str>>(i: &'a str) -> IResult<&'a str, (), E> {
    value(
        (), // Output is thrown away.
        many1(preceded(ws, delimited(tag("#"), is_not("\n\r"), opt(eol)))),
    )(i)
}
fn sp<'a, E: ParseError<&'a str>>(i: &'a str) -> IResult<&'a str, (), E> {
    value(
        (), // Output is thrown away.
        alt((comment, ws)),
    )(i)
}

fn column_align(txt: &str) -> Res<&str, ColumnAlign> {
    preceded(
        sp,
        alt((
            value(ColumnAlign::Left, tag("<")),
            value(ColumnAlign::Center, tag("^")),
            value(ColumnAlign::Right, tag(">")),
        )),
    )(txt)
}

pub fn column(txt: &str) -> Res<&str, Column> {
    let (rest, (align, (head, templ))) = context(
        "column definition",
        preceded(
            sp,
            tuple((
                opt(column_align),
                preceded(
                    sp,
                    separated_pair(
                        map(take_until("=>"), str::trim),
                        tag("=>"),
                        map(delimited(sp, take_till(|c| c == '\n'), sp), str::trim),
                    ),
                ),
            )),
        ),
    )(txt)?;
    Ok((rest, Column::new(head, templ, align)))
}

pub fn parse_table(txt: &str) -> Res<&str, Vec<Column>> {
    context(
        "table file",
        all_consuming(terminated(preceded(sp, many0(column)), sp)),
    )(txt)
}

pub fn parse_table_complete(txt: &str) -> Result<Vec<Column>, String> {
    // let's add the final line end as the file are likely to miss them
    let (_rest, val) = match parse_table(&format!("{}\n", txt)) {
        Ok(v) => v,
        Err(e) => {
            let er = match e {
                nom::Err::Error(er) | nom::Err::Failure(er) => er,
                nom::Err::Incomplete(_er) => panic!("shouldn't happen"),
            };
            return Err(convert_error(txt, er));
        }
    };
    Ok(val)
}

#[cfg(test)]
mod tests {
    use super::*;
    use rstest::rstest;

    #[rstest]
    #[case(
        "field=> test {here}",
        Column::new("field", "test {here}", Some(ColumnAlign::Center)),
        ""
    )]
    #[case(
        "<Field 1 =>{here} is {more_test?\"default\"} 2.4",
        Column::new(
            "Field 1",
            "{here} is {more_test?\"default\"} 2.4",
            Some(ColumnAlign::Left)
        ),
        ""
    )]
    #[case(
        "#new field\n < field => test {here}\n",
        Column::new("field", "test {here}", Some(ColumnAlign::Left)),
        ""
    )]
    fn column_test(#[case] txt: &str, #[case] value: Column, #[case] reminder: &str) {
        let (rest, n) = column(txt).unwrap();
        assert_eq!(rest, reminder);
        assert_eq!(n, value);
    }

    #[rstest]
    #[case(
        "field=> test {here}",
        vec![Column::new("field", "test {here}", Some(ColumnAlign::Center))],
        ""
    )]
    #[case(
        "<Field 1 =>{here} is {more_test?\"default\"} 2.4",
        vec![Column::new(
            "Field 1",
            "{here} is {more_test?\"default\"} 2.4",
            Some(ColumnAlign::Left)
        )],
        ""
    )]
    #[case(
        "#new field\n < field => test {here}\n",
        vec![Column::new("field", "test {here}", Some(ColumnAlign::Left))],
        ""
    )]
    #[case(
        "#new field\n < field => test {here}\n# an co\n\n<Field 1 =>{here} is {more_test?\"default\"} 2.4",
        vec![Column::new("field", "test {here}", Some(ColumnAlign::Left)),
	     Column::new(
		 "Field 1",
		 "{here} is {more_test?\"default\"} 2.4",
		 Some(ColumnAlign::Left)
             )],
        ""
    )]
    fn parse_table_test(#[case] txt: &str, #[case] value: Vec<Column>, #[case] reminder: &str) {
        let (rest, n) = parse_table(txt).unwrap();
        assert_eq!(rest, reminder);
        assert_eq!(n, value);
    }
}
