"""
Failed Pipeline Analysis Tool - Focused on analyzing only failed pipeline jobs

This module provides efficient analysis by focusing specifically on failed jobs:
1. Gets pipeline info and stores in database
2. Gets only failed jobs using get_failed_pipeline_jobs (more efficient)
3. Stores failed job data for fu            for job_result in job_analysis_results:
                job_result_typed = cast("dict[str, Any]", job_result)
                job_id = job_result_typed["job_id"]
                job_name = job_result_typed["job_name"]

                # Add job-specific resources
                resources["jobs_detail"][str(job_id)] = {
                    "job": f"gl://job/{project_id}/{pipeline_id}/{job_id}",
                    "errors": f"gl://errors/{project_id}/{job_id}",
                    "files": {},
                }

                # Process file groups for this job
                file_groups = cast("list[dict[str, Any]]", job_result_typed.get("file_groups", []))
                for file_group in file_groups:
Copyright (c) 2025 Siarhei Skuratovich
Licensed under the MIT License - see LICENSE file for details
"""

import hashlib
from typing import Any, cast

from fastmcp import FastMCP

from gitlab_analyzer.cache.mcp_cache import get_cache_manager
from gitlab_analyzer.cache.models import ErrorRecord
from gitlab_analyzer.core.pipeline_info import get_comprehensive_pipeline_info
from gitlab_analyzer.parsers.log_parser import LogParser
from gitlab_analyzer.parsers.pytest_parser import PytestLogParser
from gitlab_analyzer.utils.utils import (
    _should_use_pytest_parser,
    categorize_files_by_type,
    combine_exclude_file_patterns,
    extract_file_path_from_message,
    get_gitlab_analyzer,
    get_mcp_info,
    should_exclude_file_path,
)


def register_failed_pipeline_analysis_tools(mcp: FastMCP) -> None:
    """Register failed pipeline analysis tools"""

    @mcp.tool
    async def failed_pipeline_analysis(
        project_id: str | int,
        pipeline_id: int,
        store_in_db: bool = True,
        exclude_file_patterns: list[str] | None = None,
        disable_file_filtering: bool = False,
    ) -> dict[str, Any]:
        """
        🚨 FAILED PIPELINE ANALYSIS: Efficient analysis focusing only on failed jobs.

        This tool provides targeted analysis by:
        1. Gets pipeline information with branch resolution
        2. Analyzes ONLY failed jobs using get_failed_pipeline_jobs (more efficient)
        3. Stores results in database for resource access
        4. Uses caching for performance
        5. Provides structured output for failed job investigation

        WHEN TO USE:
        - Pipeline shows "failed" status and you want to focus on failures
        - More efficient than comprehensive analysis when only failures matter
        - Need failed job data stored for resource-based access
        - Want targeted investigation of specific failures

        SMART FEATURES:
        - Uses get_failed_pipeline_jobs for efficient API calls
        - Filters out non-failed jobs automatically
        - Resolves real branch names for merge request pipelines
        - Caches results for repeated access
        - Stores analysis in database for resources

        WHAT YOU GET:
        - Complete pipeline metadata with resolved branches
        - Only failed jobs analyzed (no wasted time on successful jobs)
        - Structured error and failure reason data
        - Analysis summary and statistics focused on failures
        - Resource URIs for detailed investigation

        Args:
            project_id: The GitLab project ID or path
            pipeline_id: The ID of the GitLab pipeline to analyze
            store_in_db: Whether to store results in database for resources
            exclude_file_patterns: Additional file path patterns to exclude beyond defaults.
                                 Examples: ["migrations/", "node_modules/", "vendor/"]
                                 These are combined with default system paths like .venv, site-packages, etc.
            disable_file_filtering: If True, disables all file filtering including defaults.
                                  When True, all errors from all files (including system files) are included.
                                  Useful for comprehensive debugging or when you need to see everything.

        Returns:
            Failed pipeline analysis with efficient failed-job-only parsing and caching

        WORKFLOW: Primary failed analysis tool → use resources for specific data access
        """

        try:
            analyzer = get_gitlab_analyzer()
            cache_manager = get_cache_manager()

            # Step 1: Get comprehensive pipeline info and store it
            print(f"📋 Step 1: Getting pipeline information for {pipeline_id}...")
            pipeline_info = await get_comprehensive_pipeline_info(
                analyzer=analyzer, project_id=project_id, pipeline_id=pipeline_id
            )

            if store_in_db:
                print("💾 Storing pipeline info in database...")
                # Pass the full comprehensive pipeline info (the async method now handles extraction)
                await cache_manager.store_pipeline_info_async(
                    project_id=project_id,
                    pipeline_id=pipeline_id,
                    pipeline_info=pipeline_info,
                )
                print("✅ Pipeline info stored successfully")

            # Step 2: Get only failed jobs (more efficient than all jobs)
            print("🚨 Step 2: Getting failed jobs only...")
            failed_jobs = await analyzer.get_failed_pipeline_jobs(
                project_id=project_id, pipeline_id=pipeline_id
            )

            print(f"📊 Found {len(failed_jobs)} failed jobs")

            # Step 3: Store basic failed job info in database using cache manager
            if store_in_db and failed_jobs:
                await cache_manager.store_failed_jobs_basic(
                    project_id=project_id,
                    pipeline_id=pipeline_id,
                    failed_jobs=failed_jobs,
                    pipeline_info=pipeline_info,
                )

            # Step 4: For each failed job, get trace, select parser, extract/categorize/store errors/files
            job_analysis_results = []
            # Set up file path exclusion patterns (combine defaults with user-provided patterns)
            if disable_file_filtering:
                exclude_patterns = []  # No filtering at all
                print(
                    "🚫 File filtering disabled - processing ALL files including system files"
                )
            else:
                exclude_patterns = combine_exclude_file_patterns(exclude_file_patterns)

                if exclude_file_patterns:
                    print(f"🔧 Using custom exclude patterns: {exclude_file_patterns}")
                    print(
                        f"📋 Total exclude patterns: {len(exclude_patterns)} (defaults + custom)"
                    )
                else:
                    print(f"📋 Using {len(exclude_patterns)} default exclude patterns")

            for job in failed_jobs:
                print(f"🔎 Analyzing job {job.id} ({job.name})...")
                trace = await analyzer.get_job_trace(project_id, job.id)
                parser_type = (
                    "pytest"
                    if _should_use_pytest_parser(trace, job.name, job.stage)
                    else "generic"
                )
                if parser_type == "pytest":
                    pytest_parser = PytestLogParser()
                    parsed = pytest_parser.parse_pytest_log(trace)
                    # Convert PytestFailureDetail objects to error dict format
                    errors: list[dict[str, Any]] = []
                    for failure in parsed.detailed_failures:
                        error_dict: dict[str, Any] = {
                            "exception_type": failure.exception_type,
                            "exception_message": failure.exception_message,
                            "file_path": failure.test_file,
                            "line_number": None,  # Get from traceback if available
                            "test_function": failure.test_function,
                            "test_name": failure.test_name,
                            "message": failure.exception_message,
                        }
                        # Try to get line number from traceback
                        if failure.traceback:
                            for tb in failure.traceback:
                                if tb.line_number:
                                    error_dict["line_number"] = str(tb.line_number)
                                    break
                        errors.append(error_dict)
                else:
                    log_parser = LogParser()
                    log_entries = log_parser.extract_log_entries(trace)
                    errors = [
                        {
                            "message": entry.message,
                            "level": entry.level,
                            "line_number": (
                                str(entry.line_number)
                                if entry.line_number is not None
                                else None
                            ),
                            "context": entry.context,
                        }
                        for entry in log_entries
                        if entry.level == "error"
                    ]

                # Group errors by file and filter out system files
                file_groups: dict[str, dict[str, Any]] = {}
                filtered_errors: list[
                    dict[str, Any]
                ] = []  # Track errors after filtering system files

                for error in errors:
                    message = (
                        error.get("exception_message", "")
                        or error.get("message", "")
                        or ""
                    )
                    file_path = extract_file_path_from_message(message)
                    if not file_path:
                        file_path = error.get("file_path", "unknown") or "unknown"

                    # Filter out system/exclude paths (only if filtering is enabled)
                    if not disable_file_filtering and should_exclude_file_path(
                        file_path, exclude_patterns
                    ):
                        continue  # Skip this error if the file should be excluded

                    # Keep this error since it's from an application file (or filtering is disabled)
                    filtered_errors.append(error)

                    if file_path not in file_groups:
                        file_groups[file_path] = {
                            "file_path": file_path,
                            "error_count": 0,
                            "errors": [],
                        }
                    file_groups[file_path]["error_count"] += 1
                    file_groups[file_path]["errors"].append(error)

                # Print filtering results
                original_error_count = len(errors)
                filtered_error_count = len(filtered_errors)
                filtered_out_count = original_error_count - filtered_error_count

                if filtered_out_count > 0:
                    if disable_file_filtering:
                        print(
                            f"ℹ️  No filtering applied - processed all {original_error_count} errors including system files"
                        )
                    else:
                        print(
                            f"🔽 Filtered out {filtered_out_count} errors from system files (kept {filtered_error_count}/{original_error_count})"
                        )
                elif disable_file_filtering:
                    print(
                        f"ℹ️  No filtering applied - processed all {original_error_count} errors"
                    )

                categorized = categorize_files_by_type(list(file_groups.values()))

                # Store file and error info in DB (using filtered data)
                if store_in_db:
                    # Calculate trace hash for consistency tracking
                    trace_hash = hashlib.sha256(trace.encode("utf-8")).hexdigest()

                    # Convert error dictionaries to ErrorRecord objects for trace storage
                    error_records = []
                    for i, error_dict in enumerate(filtered_errors):
                        error_record = ErrorRecord.from_parsed_error(
                            job_id=job.id, error_data=error_dict, error_index=i
                        )
                        error_records.append(error_record)

                    # Store trace segments per error with context
                    await cache_manager.store_error_trace_segments(
                        job_id=job.id,
                        trace_text=trace,
                        trace_hash=trace_hash,
                        errors=error_records,  # Use ErrorRecord objects
                        parser_type=parser_type,
                    )

                    # Store file and error analysis
                    await cache_manager.store_job_file_errors(
                        project_id=project_id,
                        pipeline_id=pipeline_id,
                        job_id=job.id,
                        files=list(file_groups.values()),
                        errors=filtered_errors,  # Use filtered errors instead of all errors
                        parser_type=parser_type,
                    )

                job_analysis_results.append(
                    {
                        "job_id": job.id,
                        "job_name": job.name,
                        "parser_type": parser_type,
                        "file_groups": list(file_groups.values()),
                        "categorized_files": categorized,
                        "errors": filtered_errors,  # Use filtered errors
                        "filtering_stats": {
                            "original_errors": original_error_count,
                            "filtered_errors": filtered_error_count,
                            "excluded_errors": filtered_out_count,
                        },
                    }
                )

            # Prepare analysis results - store in resources for later access
            # (failed_stages and failure_reasons are available in the stored data)

            # Build hierarchical resources structure with files and errors
            resources: dict[str, Any] = {
                "pipeline": f"gl://pipeline/{project_id}/{pipeline_id}",
                "jobs": f"gl://jobs/{project_id}/pipeline/{pipeline_id}",
                "analysis": f"gl://analysis/{project_id}/pipeline/{pipeline_id}",
                "files": {},
                "jobs_detail": {},
                "errors": {},
            }

            # Create file hierarchy with error links
            all_files: dict[
                str, dict[str, Any]
            ] = {}  # Global file registry across all jobs
            all_errors: dict[
                str, dict[str, Any]
            ] = {}  # Global error registry with trace references

            for job_result in job_analysis_results:
                job_result_typed = cast("dict[str, Any]", job_result)
                job_id = job_result_typed["job_id"]
                job_name = job_result_typed["job_name"]

                # Add job-specific resources
                resources["jobs_detail"][str(job_id)] = {
                    "job": f"gl://job/{project_id}/{pipeline_id}/{job_id}",
                    "errors": f"gl://errors/{project_id}/{job_id}",
                    "files": {},
                }

                # Process file groups for this job
                file_groups_data = cast(
                    "list[dict[str, Any]]", job_result_typed.get("file_groups", [])
                )
                for file_group in file_groups_data:
                    file_path = file_group["file_path"]
                    error_count = file_group["error_count"]

                    # Add individual error resources with trace references
                    errors_list = cast("list[dict[str, Any]]", file_group["errors"])
                    for i, error in enumerate(errors_list):
                        error_id = f"{job_id}_{i}"
                        error_resource_uri = (
                            f"gl://error/{project_id}/{job_id}/{error_id}"
                        )

                        # Add to global errors registry
                        all_errors[error_id] = {
                            "error": error_resource_uri,
                            "job_id": job_id,
                            "file_path": file_path,
                            "error_index": i,
                            "message": error.get("message", ""),
                            "line_number": error.get("line_number"),
                            "level": error.get("level", "error"),
                            "exception_type": error.get("exception_type"),
                            "test_function": error.get("test_function"),
                            "test_name": error.get("test_name"),
                        }

                    # Add to job-specific files
                    resources["jobs_detail"][str(job_id)]["files"][file_path] = {
                        "file": f"gl://file/{project_id}/{job_id}/{file_path.replace('/', '%2F')}",
                        "error_count": error_count,
                        "errors": f"gl://errors/{project_id}/{job_id}/{file_path.replace('/', '%2F')}",
                    }

                    # Add to global file registry (accumulate across jobs)
                    if file_path not in all_files:
                        all_files[file_path] = {
                            "path": file_path,
                            "total_error_count": 0,
                            "jobs": {},
                        }

                    all_files[file_path]["total_error_count"] += error_count
                    all_files[file_path]["jobs"][str(job_id)] = {
                        "job_name": job_name,
                        "error_count": error_count,
                        "resource": f"gl://file/{project_id}/{job_id}/{file_path.replace('/', '%2F')}",
                    }

            # Add global file hierarchy and errors to resources
            resources["files"] = all_files
            resources["errors"] = all_errors

            # Extract key information for summary
            source_branch = pipeline_info.get("source_branch") or pipeline_info.get(
                "target_branch", "unknown"
            )
            pipeline_sha = (
                pipeline_info.get("sha", "unknown")[:8]
                if pipeline_info.get("sha")
                else "unknown"
            )
            total_files = len(all_files)
            total_errors = len(all_errors)

            # Create lightweight content-based response
            content = [
                {
                    "type": "text",
                    "text": f"Analyzed pipeline {pipeline_id} ({source_branch} @ {pipeline_sha}): {len(failed_jobs)} failed jobs, {total_files} files impacted, {total_errors} errors found.",
                },
                {
                    "type": "resource_link",
                    "resourceUri": f"gl://pipeline/{project_id}/{pipeline_id}",
                    "text": "Pipeline details & metadata",
                },
                {
                    "type": "resource_link",
                    "resourceUri": f"gl://jobs/{project_id}/pipeline/{pipeline_id}",
                    "text": f"Failed jobs overview ({len(failed_jobs)} jobs)",
                },
            ]

            # Add files resource if we have files with errors
            if total_files > 0:
                # Show pagination hint for large file sets
                if total_files > 20:
                    content.append(
                        {
                            "type": "resource_link",
                            "resourceUri": f"gl://files/{project_id}/pipeline/{pipeline_id}/page/1/limit/20",
                            "text": f"Files with errors (page 1 of {(total_files + 19) // 20})",
                        }
                    )
                else:
                    content.append(
                        {
                            "type": "resource_link",
                            "resourceUri": f"gl://files/{project_id}/pipeline/{pipeline_id}",
                            "text": f"Files with errors ({total_files} files)",
                        }
                    )

            # Add errors resource if we have errors
            if total_errors > 0:
                content.append(
                    {
                        "type": "resource_link",
                        "resourceUri": f"gl://errors/{project_id}/pipeline/{pipeline_id}",
                        "text": f"Error details (page 1 of {(total_errors + 49) // 50})",
                    }
                )

            # Add analysis resource for comprehensive data
            content.append(
                {
                    "type": "resource_link",
                    "resourceUri": f"gl://analysis/{project_id}/pipeline/{pipeline_id}",
                    "text": "Complete analysis data",
                }
            )

            result = {
                "content": content,
                "mcp_info": get_mcp_info("failed_pipeline_analysis"),
            }

            print("✅ Failed pipeline analysis completed successfully")
            return result

        except (ValueError, TypeError, KeyError, RuntimeError) as e:
            print(f"❌ Error in failed pipeline analysis: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Failed to analyze pipeline {pipeline_id}: {str(e)}",
                    }
                ],
                "mcp_info": get_mcp_info("failed_pipeline_analysis", error=True),
            }
