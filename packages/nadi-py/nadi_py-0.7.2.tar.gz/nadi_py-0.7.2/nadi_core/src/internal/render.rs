use nadi_plugin::nadi_internal_plugin;

#[nadi_internal_plugin]
mod render {
    use crate::prelude::*;
    use nadi_plugin::{env_func, network_func, node_func};
    use std::path::PathBuf;
    use string_template_plus::Template;

    /// Render the template based on the node attributes
    ///
    /// If you have the safe=true, then if the rendering fails, it
    /// returns the original string template. For more details on the
    /// template system. Refer to the String Template section of the
    /// NADI book.
    ///
    /// ```task
    /// env assert_eq(render("abc {_x}", x="ab"), "abc ab")
    /// env assert_eq(render("abc {x}", x=23), "abc 23")
    /// env assert_eq(render("abc {x} {a}", safe=true), "abc {x} {a}")
    /// ```
    ///
    /// If safe parameter is true, then it doesn't error out even if
    /// the variable is not present, and will just return the original
    /// template. By default it errors out if there are any variables
    /// in the template without a value.
    ///
    /// ```task
    /// env assert_eq(render("abc {x}", safe=true), "abc {x}")
    /// ```
    #[env_func(safe = false)]
    fn render(
        /// String template to render
        template: &Template,
        /// if render fails keep it as it is instead of exiting
        safe: bool,
        #[kwargs] keyval: &AttrMap,
    ) -> Result<String, String> {
        let text = if safe {
            keyval
                .render(template)
                .unwrap_or_else(|_| template.original().to_string())
        } else {
            keyval.render(template).map_err(|e| e.to_string())?
        };
        Ok(text)
    }

    /// Render the template based on the node attributes
    ///
    /// For more details on the template system. Refer to the String
    /// Template section of the NADI book.
    ///
    /// ```task
    /// network load_str("a -> b")
    /// node.x = 13
    /// node assert_eq(render("abc {x}"), "abc 13")
    /// node assert_eq(render("abc {x} {a}", safe=true), "abc {x} {a}")
    /// ```
    #[node_func(safe = false)]
    fn render(
        node: &NodeInner,
        /// String template to render
        template: &Template,
        /// if render fails keep it as it is instead of exiting
        safe: bool,
    ) -> Result<String, String> {
        let text = if safe {
            node.render(template)
                .unwrap_or_else(|_| template.original().to_string())
        } else {
            node.render(template).map_err(|e| e.to_string())?
        };
        Ok(text)
    }

    /// Render from network attributes
    ///
    /// ```task
    /// network.x = 13
    /// network assert_eq(render("abc {x}"), "abc 13")
    /// network assert_eq(render("abc {x} {a}", safe=true), "abc {x} {a}")
    /// ```
    #[network_func(safe = false)]
    fn render(
        network: &Network,
        /// Path to the template file
        template: &Template,
        /// if render fails keep it as it is instead of exiting
        safe: bool,
    ) -> Result<String, String> {
        let text = if safe {
            network
                .render(template)
                .unwrap_or_else(|_| template.original().to_string())
        } else {
            network.render(template).map_err(|e| e.to_string())?
        };
        Ok(text)
    }

    /// Render each node of the network and combine to same variable
    ///
    /// ```task
    /// network load_str("a -> b")
    /// node.x = INDEX + 1
    /// network assert_eq(render_nodes("abc {x}"), "abc 1\nabc 2")
    /// ```
    #[network_func(safe = false, join = "\n")]
    fn render_nodes(
        network: &Network,
        /// Path to the template file
        template: &Template,
        /// if render fails keep it as it is instead of exiting
        safe: bool,
        /// String to join the render results
        join: &str,
    ) -> Result<String, String> {
        let lines: Vec<String> = network
            .nodes()
            .map(|n| {
                let node = n.lock();
                if safe {
                    Ok(node
                        .render(template)
                        .unwrap_or_else(|_| template.original().to_string()))
                } else {
                    node.render(template).map_err(|e| e.to_string())
                }
            })
            .collect::<Result<Vec<_>, String>>()?;
        Ok(lines.join(join))
    }

    /// Render a File template for the nodes in the whole network
    ///
    /// Write the file with templates for input variables in the same
    /// way you write string templates. It's useful for markdown
    /// files, as the curly braces syntax won't be used for anything
    /// else that way. Do be careful about that. And the program will
    /// replace those templates with their values when you run it with
    /// inputs.
    ///
    /// It'll repeat the same template for each node and render them.
    /// If you want only a portion of the file repeated for nodes
    /// inclose them with lines with `---8<---` on both start and the
    /// end. The lines containing the clip syntax will be ignored,
    /// ideally you can put them in comments.
    ///
    /// You can also use `---include:<filename>[::line_range]` syntax to
    /// include a file, the line_range syntax, if present, should be
    /// in the form of `start[:increment]:end`, you can exclude start
    /// or end to denote the line 1 or last line (e.g. `:5` is 1:5,
    /// and `3:` is from line 3 to the end)
    ///
    /// # Arguments
    /// - `template`: Path to the template file
    /// - `outfile` [Optional]: Path to save the template file, if none it'll be printed in stdout
    #[network_func]
    fn render_template(
        network: &Network,
        /// Path to the template file
        template: PathBuf,
    ) -> anyhow::Result<String> {
        let template = super::render_utils::RenderFileContents::read_file(&template)?;
        template.render(network)
    }
}

mod render_utils {
    use crate::network::Propagation;
    use crate::prelude::*;
    use anyhow::{Context, Error};
    use number_range::NumberRangeOptions;

    use std::fs::File;
    use std::io::{BufRead, BufReader};
    use std::path::{Path, PathBuf};
    use std::str::FromStr;
    use string_template_plus::Template;

    pub enum RenderFileContentsType {
        Include(PathBuf, String),
        Literal(String),
        Snippet(Template, Propagation),
    }

    pub struct RenderFileContents {
        contents: Vec<RenderFileContentsType>,
    }

    fn insert_till_now(
        lines: &mut String,
        batch: Option<Propagation>,
        filecontents: &mut RenderFileContents,
    ) -> Result<(), Error> {
        let p = if let Some(batch) = batch {
            RenderFileContentsType::Snippet(Template::parse_template(lines)?, batch)
        } else {
            RenderFileContentsType::Literal(lines.clone())
        };
        filecontents.contents.push(p);
        lines.clear();
        Ok(())
    }

    impl RenderFileContents {
        pub fn read_file(filename: &Path) -> Result<Self, Error> {
            let file = match File::open(filename) {
                Ok(f) => f,
                Err(e) => {
                    return Err(Error::msg(format!(
                        "Couldn't open input file: {:?}\n{:?}",
                        filename.to_string_lossy(),
                        e
                    )));
                }
            };
            let reader_lines = BufReader::new(file).lines();

            let mut snippet = false;
            let mut filecontents = RenderFileContents {
                contents: Vec::new(),
            };
            let mut lines = String::new();
            let mut batch: Option<Propagation> = None;
            for line in reader_lines {
                let l = line.unwrap();
                if l.contains("---8<---") {
                    insert_till_now(&mut lines, batch.clone(), &mut filecontents)?;
                    batch = if snippet {
                        // if in a snippet already, we're exiting
                        None
                    } else if let Some((_, s)) = l.split_once(':') {
                        let s = s.split_once(':').map(|(s, _)| s).unwrap_or(s);
                        let prop = Propagation::from_str(s)?;
                        Some(prop)
                    } else {
                        Some(Propagation::default())
                    };
                    snippet = !snippet;
                } else if l.contains("---include:") {
                    if snippet {
                        // todo let it include files globally, as well as inside snippets
                        return Err(Error::msg("Cannot have file in render snippet"));
                    }
                    insert_till_now(&mut lines, None, &mut filecontents)?;
                    let (_, fname) = l.split_once(':').unwrap();
                    let (fname, lines) = fname.split_once("::").unwrap_or((fname, ":"));
                    filecontents.contents.push(RenderFileContentsType::Include(
                        PathBuf::from(filename).parent().unwrap().join(fname.trim()),
                        lines.to_string(),
                    ))
                } else {
                    lines.push_str(&l);
                    lines.push('\n');
                }
            }
            if filecontents.contents.is_empty() {
                // if there is no ---8<--- in file, consider the whole
                // file as snippet
                batch = Some(Propagation::default());
            }
            if !lines.is_empty() {
                insert_till_now(&mut lines, batch, &mut filecontents)?;
            }
            Ok(filecontents)
        }

        fn _snippet(templ: &str, batch: Propagation) -> Result<Self, Error> {
            Ok(Self {
                contents: vec![RenderFileContentsType::Snippet(
                    Template::parse_template(templ)?,
                    batch,
                )],
            })
        }

        pub fn render(&self, net: &Network) -> anyhow::Result<String> {
            let mut output = String::new();
            for part in &self.contents {
                match part {
                    RenderFileContentsType::Include(filename, lines) => {
                        let file = File::open(filename)
                            .with_context(|| format!("File {filename:?} not found"))?;
                        let reader_lines: Vec<String> = BufReader::new(file)
                            .lines()
                            .collect::<Result<Vec<String>, std::io::Error>>()?;
                        let lines = NumberRangeOptions::default()
                            .with_default_start(1)
                            .with_default_end(reader_lines.len())
                            .parse(lines)?;
                        for l in lines {
                            output.push_str(&reader_lines[l - 1]);
                            output.push('\n');
                        }
                    }
                    RenderFileContentsType::Literal(s) => output.push_str(s),
                    RenderFileContentsType::Snippet(templ, prop) => {
                        for node in net
                            .nodes_select(&prop.order, &prop.nodes)
                            .map_err(anyhow::Error::msg)?
                        {
                            output.push_str(&node.lock().render(templ)?);
                        }
                    }
                }
            }
            Ok(output)
        }
    }
}
