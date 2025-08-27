use nadi_plugin::nadi_internal_plugin;

#[nadi_internal_plugin]
mod table {

    use crate::prelude::*;
    use crate::table::Table;

    use nadi_plugin::network_func;
    use std::path::PathBuf;
    use std::str::FromStr;

    use std::{fs::File, io::Write, path::Path};

    /// Save CSV
    #[network_func]
    fn save_csv(
        net: &Network,
        path: &Path,
        fields: &[String],
        filter: Option<Vec<bool>>,
    ) -> anyhow::Result<()> {
        let mut file = File::create(path)?;
        writeln!(file, "{}", fields.join(","))?;
        let nodes: Vec<_> = match filter {
            Some(filt) => net
                .nodes()
                .zip(filt)
                .filter(|(_, f)| *f)
                .map(|(n, _)| n)
                .collect(),
            None => net.nodes().collect(),
        };
        for node in nodes {
            let values = fields
                .iter()
                .map(|a| {
                    node.lock().attr_dot(a).map(|a| match a {
                        Some(v) => v.to_string(),
                        None => String::new(),
                    })
                })
                .collect::<Result<Vec<String>, String>>()
                .map_err(anyhow::Error::msg)?;
            writeln!(file, "{}", values.join(","))?;
        }
        Ok(())
    }

    /** Render the Table as a rendered markdown

    # Error
    The function will error out if,
    - error reading the table file,
    - error parsing table template,
    - neither one of table file or table template is provided,
    - error while rendering markdown
      (caused by error on rendering cell values from templates)
    - error while writing to the output file
    */
    #[network_func]
    fn table_to_markdown(
        net: &Network,
        /// Path to the table file
        table: Option<PathBuf>,
        /// String template for table
        template: Option<String>,
        /// Path to the output file
        outfile: Option<PathBuf>,
        /// Show connections column or not
        connections: Option<String>,
    ) -> anyhow::Result<()> {
        let tab = match (table, template) {
            (Some(t), None) => Table::from_file(t)?,
            (None, Some(t)) => Table::from_str(&t)?,
            (Some(_), Some(_)) => return Err(anyhow::Error::msg("table and template both given")),
            (None, None) => return Err(anyhow::Error::msg("neither table nor template given")),
        };
        let md = tab.render_markdown(net, connections)?;
        if let Some(out) = outfile {
            let mut output = std::fs::File::create(out)?;
            write!(output, "{md}")?;
        } else {
            println!("{md}");
        }
        Ok(())
    }
}
