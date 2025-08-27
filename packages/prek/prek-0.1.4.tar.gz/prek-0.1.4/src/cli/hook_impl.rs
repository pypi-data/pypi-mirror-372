use std::ffi::OsString;
use std::path::PathBuf;

use anstream::eprintln;
use anyhow::Result;
use owo_colors::OwoColorize;

use constants::env_vars::EnvVars;

use crate::cli::{self, ExitStatus, RunArgs};
use crate::config::HookType;
use crate::printer::Printer;

pub(crate) async fn hook_impl(
    config: Option<PathBuf>,
    hook_type: HookType,
    _hook_dir: PathBuf,
    skip_on_missing_config: bool,
    args: Vec<OsString>,
    printer: Printer,
) -> Result<ExitStatus> {
    // TODO: run in legacy mode

    if let Some(ref config_file) = config {
        if !config_file.try_exists()? {
            return if skip_on_missing_config || EnvVars::is_set(EnvVars::PREK_ALLOW_NO_CONFIG) {
                Ok(ExitStatus::Success)
            } else {
                eprintln!(
                    "{}: config file not found: `{}`",
                    "error".red().bold(),
                    config_file.display().cyan()
                );
                eprintln!(
                    "- To temporarily silence this, run `{}`",
                    format!("{}=1 git ...", EnvVars::PREK_ALLOW_NO_CONFIG).cyan()
                );
                eprintln!(
                    "- To permanently silence this, install hooks with the `{}` flag",
                    "--allow-missing-config".cyan()
                );
                eprintln!("- To uninstall hooks, run `{}`", "prek uninstall".cyan());
                Ok(ExitStatus::Failure)
            };
        }
    }

    if !hook_type.num_args().contains(&args.len()) {
        eprintln!("Invalid number of arguments for hook: {}", hook_type);
        return Ok(ExitStatus::Failure);
    }

    let run_args = to_run_args(hook_type, &args);

    cli::run(
        config,
        run_args.hook_ids,
        hook_type.into(),
        run_args.from_ref,
        run_args.to_ref,
        run_args.all_files,
        vec![],
        vec![],
        false, // last_commit is always false in hook implementation context
        false,
        run_args.extra,
        false,
        printer,
    )
    .await
}

fn to_run_args(hook_type: HookType, args: &[OsString]) -> RunArgs {
    let mut run_args = RunArgs::default();

    match hook_type {
        HookType::PrePush => {
            run_args.extra.remote_name = Some(args[0].to_string_lossy().into_owned());
            run_args.extra.remote_url = Some(args[1].to_string_lossy().into_owned());
            // TODO: implement pre-push
        }
        HookType::CommitMsg => {
            run_args.extra.commit_msg_filename = Some(args[0].to_string_lossy().into_owned());
        }
        HookType::PrepareCommitMsg => {
            run_args.extra.commit_msg_filename = Some(args[0].to_string_lossy().into_owned());
            if args.len() > 1 {
                run_args.extra.prepare_commit_message_source =
                    Some(args[1].to_string_lossy().into_owned());
            }
            if args.len() > 2 {
                run_args.extra.commit_object_name = Some(args[2].to_string_lossy().into_owned());
            }
        }
        HookType::PostCheckout => {
            run_args.from_ref = Some(args[0].to_string_lossy().into_owned());
            run_args.to_ref = Some(args[1].to_string_lossy().into_owned());
            run_args.extra.checkout_type = Some(args[2].to_string_lossy().into_owned());
        }
        HookType::PostMerge => run_args.extra.is_squash_merge = args[0] == "1",
        HookType::PostRewrite => {
            run_args.extra.rewrite_command = Some(args[0].to_string_lossy().into_owned());
        }
        HookType::PreRebase => {
            run_args.extra.pre_rebase_upstream = Some(args[0].to_string_lossy().into_owned());
            if args.len() > 1 {
                run_args.extra.pre_rebase_branch = Some(args[1].to_string_lossy().into_owned());
            }
        }
        HookType::PostCommit | HookType::PreMergeCommit | HookType::PreCommit => {}
    }

    run_args
}
