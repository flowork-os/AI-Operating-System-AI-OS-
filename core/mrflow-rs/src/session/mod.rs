use crate::config::{resolve_project_slug, AppConfig};
use crate::inference::{ChatMessage, ContentPart, FunctionCallData, TokenUsage};
use base64::{engine::general_purpose::STANDARD as B64, Engine as _};
use chrono::Utc;
use rusqlite::{params, Connection};
use serde_json::{json, Value};
use std::collections::{HashMap, HashSet, VecDeque};
use std::fs::{self, File, OpenOptions};
use std::io::{BufRead, BufReader, Read, Seek, SeekFrom, Write};
use std::path::{Path, PathBuf};
use uuid::Uuid;

#[derive(Debug, Clone)]
pub struct SessionSummary {
    pub index: usize,
    pub session_id: String,
    pub path: PathBuf,
    #[allow(dead_code)]
    pub start_time: String,
    pub last_updated: String,
    pub preview: String,
}

#[derive(Debug, Clone)]
pub struct SessionVault {
    pub session_id: String,
    pub slug: String,
    pub path: PathBuf,
    pub compact_path: PathBuf,
    pub summary_db_path: Option<PathBuf>,
    #[allow(dead_code)]
    pub project_hash: String,
}

pub fn compact_path_for(full_path: &Path) -> PathBuf {
    let parent = full_path.parent().unwrap_or_else(|| Path::new("."));
    let fname = full_path
        .file_name()
        .and_then(|s| s.to_str())
        .unwrap_or("session.jsonl");
    parent.join(".compact").join(fname)
}

pub fn summary_db_path_for(full_path: &Path) -> Option<PathBuf> {
    let slug_dir = full_path.parent()?;
    let chats_dir = slug_dir.parent()?;
    Some(chats_dir.join("session_summaries.db"))
}

impl SessionVault {
    pub fn open_or_create(config: &AppConfig) -> Result<(Self, Vec<ChatMessage>), String> {
        let slug = resolve_project_slug(&config.cwd, &config.paths.user_flowork_dir);
        let project_hash = simple_sha_hex(&config.cwd.to_string_lossy());

        if let Some(ref custom_file) = config.session_file {
            if custom_file.is_file() {
                let (sid, history) = load_jsonl_session(custom_file)?;
                let compact_path = compact_path_for(custom_file);
                if !compact_path.exists() {
                    let _ = backfill_compact_transcript(custom_file, &compact_path);
                }
                let summary_db_path = summary_db_path_for(custom_file);
                let vault = Self {
                    session_id: sid,
                    slug,
                    path: custom_file.clone(),
                    compact_path,
                    summary_db_path,
                    project_hash,
                };
                vault.update_latest_symlink(config);
                return Ok((vault, history));
            }
        }

        if let Some(ref resume_spec) = config.resume {
            let summaries = list_sessions(config);
            if let Some(found) = find_matching_session(config, &summaries, resume_spec) {
                let (sid, history) = load_jsonl_session(&found.path)?;
                let compact_path = compact_path_for(&found.path);
                if !compact_path.exists() {
                    let _ = backfill_compact_transcript(&found.path, &compact_path);
                }
                let summary_db_path = summary_db_path_for(&found.path);
                let vault = Self {
                    session_id: sid,
                    slug,
                    path: found.path,
                    compact_path,
                    summary_db_path,
                    project_hash,
                };
                vault.update_latest_symlink(config);
                return Ok((vault, history));
            } else if resume_spec != "latest" {
                return Err(format!(
                    "Session '{}' not found in project '{}'. Use --list-sessions to view available sessions.",
                    resume_spec, slug
                ));
            }
        }

        let session_id = config
            .session_id
            .clone()
            .filter(|s| !s.trim().is_empty())
            .unwrap_or_else(|| Uuid::new_v4().to_string());
        let short8: String = session_id.chars().filter(|c| c.is_ascii_hexdigit()).take(8).collect();
        let now = Utc::now();
        let fname = format!(
            "session-{}-{}.jsonl",
            now.format("%Y-%m-%dT%H-%M"),
            if short8.is_empty() { "flowork0".to_string() } else { short8 }
        );

        let dir = config.paths.history_chats_dir.join(&slug);
        fs::create_dir_all(&dir).map_err(|e| format!("Failed creating chat vault dir: {}", e))?;
        let compact_dir = dir.join(".compact");
        let _ = fs::create_dir_all(&compact_dir);
        let path = dir.join(&fname);
        let compact_path = compact_dir.join(&fname);
        let summary_db_path = Some(config.paths.history_chats_dir.join("session_summaries.db"));

        let now_iso = now.to_rfc3339_opts(chrono::SecondsFormat::Millis, true);
        let header = json!({
            "sessionId": session_id,
            "projectHash": project_hash,
            "startTime": now_iso,
            "lastUpdated": now_iso,
            "kind": "main"
        });
        append_json_line(&path, &header)?;
        let _ = append_json_line(&compact_path, &header);

        if let Some(ref db_path) = summary_db_path {
            let fsize = fs::metadata(&path).map(|m| m.len() as i64).unwrap_or(0);
            let _ = db_upsert_session(
                db_path,
                &session_id,
                &slug,
                &path,
                &compact_path,
                "New Session",
                "New Session",
                &now_iso,
                &now_iso,
                0,
                false,
                fsize,
            );
        }

        let vault = Self {
            session_id,
            slug,
            path,
            compact_path,
            summary_db_path,
            project_hash,
        };
        vault.update_latest_symlink(config);
        Ok((vault, Vec::new()))
    }

    pub fn update_latest_symlink(&self, config: &AppConfig) {
        let hist_root = config.paths.user_flowork_dir.join("history");
        let _ = fs::create_dir_all(&hist_root);
        let link = hist_root.join("latest_session");
        let _ = fs::remove_file(&link);
        #[cfg(unix)]
        {
            let _ = std::os::unix::fs::symlink(&self.path, &link);
        }
    }

    pub fn append_user_prompt(&self, text: &str) -> Result<(), String> {
        let ts = Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Millis, true);
        let rec = json!({
            "id": Uuid::new_v4().to_string(),
            "timestamp": ts,
            "type": "user",
            "content": [{ "text": text }]
        });
        append_json_line(&self.path, &rec)?;
        let compact_rec = compact_record_from_full(&rec);
        let _ = append_json_line(&self.compact_path, &compact_rec);

        if let Some(ref db_path) = self.summary_db_path {
            let preview_clean: String = text
                .split_whitespace()
                .collect::<Vec<_>>()
                .join(" ")
                .chars()
                .take(120)
                .collect();
            let fsize = fs::metadata(&self.path).map(|m| m.len() as i64).unwrap_or(0);
            let _ = db_record_user_prompt(
                db_path,
                &self.session_id,
                &self.slug,
                &self.path,
                &self.compact_path,
                &preview_clean,
                &ts,
                fsize,
            );
        }
        self.touch_updated(&ts)
    }

    pub fn append_tool_responses(&self, parts: &[ContentPart]) -> Result<(), String> {
        let ts = Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Millis, true);
        let rec = json!({
            "id": Uuid::new_v4().to_string(),
            "timestamp": ts,
            "type": "user",
            "content": parts
        });
        append_json_line(&self.path, &rec)?;
        let compact_rec = compact_record_from_full(&rec);
        let _ = append_json_line(&self.compact_path, &compact_rec);
        self.touch_updated(&ts)
    }

    pub fn append_model_turn(
        &self,
        model: &str,
        text: &str,
        thoughts: &[String],
        tokens: &TokenUsage,
        tool_calls_log: &[Value],
        raw_parts: &[ContentPart],
    ) -> Result<(), String> {
        let ts = Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Millis, true);
        let thought_objs: Vec<Value> = thoughts
            .iter()
            .filter(|t| !t.trim().is_empty())
            .map(|t| {
                json!({
                    "subject": "",
                    "description": t
                })
            })
            .collect();

        let coalesced_raw = crate::context::coalesce_parts(raw_parts.to_vec());

        let mut rec = json!({
            "id": Uuid::new_v4().to_string(),
            "timestamp": ts,
            "type": "gemini",
            "content": text,
            "thoughts": thought_objs,
            "tokens": {
                "input": tokens.input,
                "output": tokens.output,
                "cached": tokens.cached,
                "thoughts": tokens.thoughts,
                "tool": 0,
                "total": tokens.total
            },
            "model": model,
            "rawParts": coalesced_raw
        });
        if !tool_calls_log.is_empty() {
            rec["toolCalls"] = json!(tool_calls_log);
        }
        append_json_line(&self.path, &rec)?;
        let compact_rec = compact_record_from_full(&rec);
        let _ = append_json_line(&self.compact_path, &compact_rec);

        if let Some(ref db_path) = self.summary_db_path {
            let has_err = tool_calls_log.iter().any(|tc| {
                tc.get("status")
                    .and_then(|s| s.as_str())
                    .map(|s| s.eq_ignore_ascii_case("error"))
                    .unwrap_or(false)
            });
            let fsize = fs::metadata(&self.path).map(|m| m.len() as i64).unwrap_or(0);
            let _ = db_record_model_turn(
                db_path,
                &self.session_id,
                &self.slug,
                &self.path,
                &self.compact_path,
                &ts,
                has_err,
                fsize,
            );
        }
        self.touch_updated(&ts)
    }

    /// Appends a dual compact checkpoint into the append-only JSONL ledger without deleting original turns.
    /// Original turns stay intact ("versi utuh") for forensics & Sidebar; `--resume` loads the compressed anchor.
    pub fn append_compression_snapshot(
        &self,
        snapshot_text: &str,
        preserved_tail: &[ChatMessage],
        original_token_count: u64,
        new_token_count: u64,
    ) -> Result<(), String> {
        let ts = Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Millis, true);
        let rec = json!({
            "id": Uuid::new_v4().to_string(),
            "timestamp": ts,
            "type": "compression_snapshot",
            "snapshot": snapshot_text,
            "preservedTail": preserved_tail,
            "originalTokenCount": original_token_count,
            "newTokenCount": new_token_count
        });
        append_json_line(&self.path, &rec)?;
        let compact_rec = compact_record_from_full(&rec);
        let _ = append_json_line(&self.compact_path, &compact_rec);
        self.touch_updated(&ts)
    }

    pub fn append_summary(&self, summary: &str) -> Result<(), String> {
        let clean: String = summary.trim().chars().take(120).collect();
        if clean.is_empty() {
            return Ok(());
        }
        let rec = json!({ "$set": { "summary": clean } });
        append_json_line(&self.path, &rec)?;
        let _ = append_json_line(&self.compact_path, &rec);
        if let Some(ref db_path) = self.summary_db_path {
            let _ = db_update_summary_title(db_path, &self.session_id, &clean);
        }
        Ok(())
    }

    pub fn append_rewind(&self, keep_history_len: usize) -> Result<(), String> {
        let ts = Utc::now().to_rfc3339_opts(chrono::SecondsFormat::Millis, true);
        let rec = json!({
            "timestamp": ts,
            "$rewind": { "keepCount": keep_history_len }
        });
        append_json_line(&self.path, &rec)?;
        let _ = append_json_line(&self.compact_path, &rec);
        self.touch_updated(&ts)
    }

    fn touch_updated(&self, ts: &str) -> Result<(), String> {
        let rec = json!({ "$set": { "lastUpdated": ts } });
        append_json_line(&self.path, &rec)?;
        let _ = append_json_line(&self.compact_path, &rec);
        if let Some(ref db_path) = self.summary_db_path {
            let fsize = fs::metadata(&self.path).map(|m| m.len() as i64).unwrap_or(0);
            let _ = db_touch_updated(db_path, &self.session_id, ts, fsize);
        }
        Ok(())
    }

    pub fn save_checkpoint(&self, config: &AppConfig, tag: &str, history: &[ChatMessage]) -> Result<PathBuf, String> {
        let dir = config.paths.checkpoints_dir.join(&self.slug);
        fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
        let safe_tag: String = tag
            .chars()
            .map(|c| if c.is_ascii_alphanumeric() || c == '-' || c == '_' { c } else { '_' })
            .collect();
        let file = dir.join(format!("{}.json", if safe_tag.is_empty() { "default" } else { &safe_tag }));
        let data = serde_json::to_string_pretty(&json!({
            "tag": tag,
            "session_id": self.session_id,
            "saved_at": Utc::now().to_rfc3339(),
            "history": history
        }))
        .map_err(|e| e.to_string())?;
        fs::write(&file, data).map_err(|e| e.to_string())?;
        Ok(file)
    }

    pub fn restore_checkpoint(&self, config: &AppConfig, tag: &str) -> Result<Vec<ChatMessage>, String> {
        let dir = config.paths.checkpoints_dir.join(&self.slug);
        let safe_tag: String = tag
            .chars()
            .map(|c| if c.is_ascii_alphanumeric() || c == '-' || c == '_' { c } else { '_' })
            .collect();
        let file = dir.join(format!("{}.json", if safe_tag.is_empty() { "default" } else { &safe_tag }));
        let raw = fs::read_to_string(&file).map_err(|e| format!("Checkpoint '{}' not found: {}", tag, e))?;
        let val: Value = serde_json::from_str(&raw).map_err(|e| e.to_string())?;
        let hist: Vec<ChatMessage> = serde_json::from_value(val.get("history").cloned().unwrap_or(json!([])))
            .map_err(|e| e.to_string())?;
        Ok(hist)
    }

    pub fn list_checkpoints(&self, config: &AppConfig) -> Vec<String> {
        let dir = config.paths.checkpoints_dir.join(&self.slug);
        let Ok(entries) = fs::read_dir(dir) else {
            return Vec::new();
        };
        let mut names: Vec<String> = entries
            .flatten()
            .filter_map(|e| {
                let p = e.path();
                if p.extension().and_then(|s| s.to_str()) == Some("json") {
                    p.file_stem().and_then(|s| s.to_str()).map(str::to_string)
                } else {
                    None
                }
            })
            .collect();
        names.sort();
        names
    }
}

fn append_json_line(path: &Path, val: &Value) -> Result<(), String> {
    if let Some(parent) = path.parent() {
        if !parent.exists() {
            let _ = fs::create_dir_all(parent);
        }
    }
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)
        .map_err(|e| format!("Open session JSONL error: {}", e))?;
    let line = serde_json::to_string(val).map_err(|e| e.to_string())?;
    writeln!(file, "{}", line).map_err(|e| format!("Write session JSONL error: {}", e))?;
    Ok(())
}

pub fn load_jsonl_session(path: &Path) -> Result<(String, Vec<ChatMessage>), String> {
    let file = File::open(path).map_err(|e| format!("Cannot open session file: {}", e))?;
    let reader = BufReader::new(file);
    let mut session_id = String::new();
    let mut history: Vec<ChatMessage> = Vec::new();

    for line in reader.lines().map_while(Result::ok) {
        let t = line.trim();
        if t.is_empty() {
            continue;
        }
        let Ok(v) = serde_json::from_str::<Value>(t) else {
            continue;
        };
        if let Some(sid) = v.get("sessionId").and_then(|s| s.as_str()) {
            session_id = sid.to_string();
            continue;
        }
        if v.get("$set").is_some() {
            continue;
        }
        if let Some(rw) = v.get("$rewind") {
            if let Some(keep) = rw.get("keepCount").and_then(|k| k.as_u64()) {
                history.truncate(keep as usize);
            }
            continue;
        }
        match v.get("type").and_then(|s| s.as_str()) {
            Some("compression_snapshot") => {
                if let Some(snap) = v.get("snapshot").and_then(|s| s.as_str()) {
                    history.clear();
                    history.push(ChatMessage {
                        role: "user".to_string(),
                        parts: vec![ContentPart::text(snap.to_string())],
                    });
                    history.push(ChatMessage {
                        role: "model".to_string(),
                        parts: vec![ContentPart::text(
                            "Understood. Continuing seamlessly from the compressed state snapshot.",
                        )],
                    });
                    if let Some(tail) = v.get("preservedTail").and_then(|t| t.as_array()) {
                        for item in tail {
                            if let Ok(msg) = serde_json::from_value::<ChatMessage>(item.clone()) {
                                history.push(msg);
                            }
                        }
                    }
                }
            }
            Some("user") => {
                if let Some(arr) = v.get("content").and_then(|c| c.as_array()) {
                    let mut parts = Vec::new();
                    for item in arr {
                        if let Ok(mut p) = serde_json::from_value::<ContentPart>(item.clone()) {
                            if let Some(ref mut fr) = p.function_response {
                                if let Some(resp) = fr.get_mut("response") {
                                    if !resp.is_object() {
                                        *resp = json!({ "output": resp.clone() });
                                    }
                                }
                            }
                            if let Some(ref txt) = p.text {
                                // Skip verbose internal system telemetry wrappers on resume, keep real user prompts
                                if txt.starts_with("<session_context>") {
                                    continue;
                                }
                            }
                            parts.push(p);
                        } else if let Some(txt) = item.get("text").and_then(|s| s.as_str()) {
                            parts.push(ContentPart::text(txt));
                        }
                    }
                    if !parts.is_empty() {
                        history.push(ChatMessage {
                            role: "user".to_string(),
                            parts,
                        });
                    }
                } else if let Some(txt) = v.get("content").and_then(|c| c.as_str()) {
                    history.push(ChatMessage {
                        role: "user".to_string(),
                        parts: vec![ContentPart::text(txt)],
                    });
                }
            }
            Some("gemini") => {
                if let Some(raw_arr) = v.get("rawParts").and_then(|c| c.as_array()) {
                    let mut parts = Vec::new();
                    for item in raw_arr {
                        if let Ok(p) = serde_json::from_value::<ContentPart>(item.clone()) {
                            parts.push(p);
                        }
                    }
                    if !parts.is_empty() {
                        history.push(ChatMessage {
                            role: "model".to_string(),
                            parts,
                        });
                        continue;
                    }
                }
                // Backward-compatible reconstruction from legacy JSONL
                let mut parts = Vec::new();
                if let Some(txt) = v.get("content").and_then(|c| c.as_str()) {
                    if !txt.is_empty() {
                        parts.push(ContentPart::text(txt));
                    }
                }
                if let Some(tcs) = v.get("toolCalls").and_then(|a| a.as_array()) {
                    for tc in tcs {
                        let id = tc.get("id").and_then(|s| s.as_str()).unwrap_or("call_0").to_string();
                        let name = tc.get("name").and_then(|s| s.as_str()).unwrap_or("").to_string();
                        let args = tc.get("args").cloned().unwrap_or_else(|| json!({}));
                        if !name.is_empty() {
                            parts.push(ContentPart {
                                text: None,
                                thought: None,
                                thought_signature: None,
                                function_call: Some(FunctionCallData { id, name, args }),
                                function_response: None,
                                inline_data: None,
                            });
                        }
                    }
                }
                if !parts.is_empty() {
                    history.push(ChatMessage {
                        role: "model".to_string(),
                        parts,
                    });
                }
            }
            _ => {}
        }
    }

    if session_id.is_empty() {
        session_id = Uuid::new_v4().to_string();
    }
    Ok((session_id, history))
}

pub fn list_sessions(config: &AppConfig) -> Vec<SessionSummary> {
    let slug = resolve_project_slug(&config.cwd, &config.paths.user_flowork_dir);
    let project_dir = config.paths.history_chats_dir.join(&slug);
    let db_path = config.paths.history_chats_dir.join("session_summaries.db");

    let mut disk_files: Vec<PathBuf> = Vec::new();
    if let Ok(entries) = fs::read_dir(&project_dir) {
        for entry in entries.flatten() {
            let p = entry.path();
            if p.is_file() && p.extension().and_then(|s| s.to_str()) == Some("jsonl") {
                disk_files.push(p);
            }
        }
    }

    let disk_set: HashSet<String> = disk_files
        .iter()
        .map(|p| p.to_string_lossy().to_string())
        .collect();

    let mut db_rows = db_list_sessions_for_slug(&db_path, &slug).unwrap_or_default();
    let mut indexed_paths: HashMap<String, (String, i64)> = HashMap::new();
    for row in &db_rows {
        indexed_paths.insert(row.file_path.clone(), (row.session_id.clone(), row.file_size));
    }

    // Prune deleted files from SQLite index
    let mut pruned = false;
    for row in &db_rows {
        if !disk_set.contains(&row.file_path) {
            let _ = db_delete_session(&db_path, &row.session_id);
            pruned = true;
        }
    }

    // Backfill any unindexed or externally modified files into SQLite index
    let mut backfilled = false;
    for p in &disk_files {
        let p_str = p.to_string_lossy().to_string();
        let cur_size = fs::metadata(p).map(|m| m.len() as i64).unwrap_or(0);
        let needs_index = match indexed_paths.get(&p_str) {
            Some((_, prev_size)) => *prev_size != cur_size,
            None => true,
        };
        if needs_index {
            if let Some(sum) = summarize_session_file(1, p) {
                let compact_p = compact_path_for(p);
                let title = if sum.preview.is_empty() {
                    "New Session".to_string()
                } else {
                    sum.preview.clone()
                };
                let _ = db_upsert_session(
                    &db_path,
                    &sum.session_id,
                    &slug,
                    p,
                    &compact_p,
                    &title,
                    &sum.preview,
                    &sum.start_time,
                    &sum.last_updated,
                    0,
                    false,
                    cur_size,
                );
                backfilled = true;
            }
        }
    }

    if pruned || backfilled {
        db_rows = db_list_sessions_for_slug(&db_path, &slug).unwrap_or_default();
    }

    if !db_rows.is_empty() {
        db_rows.sort_by(|a, b| {
            b.last_updated
                .cmp(&a.last_updated)
                .then_with(|| b.file_path.cmp(&a.file_path))
        });
        return db_rows
            .into_iter()
            .enumerate()
            .map(|(idx, r)| SessionSummary {
                index: idx + 1,
                session_id: r.session_id,
                path: PathBuf::from(r.file_path),
                start_time: r.start_time,
                last_updated: r.last_updated,
                preview: r.preview,
            })
            .collect();
    }

    // Fallback if DB unavailable
    disk_files.sort_by(|a, b| {
        let ma = fs::metadata(a).and_then(|m| m.modified()).ok();
        let mb = fs::metadata(b).and_then(|m| m.modified()).ok();
        mb.cmp(&ma).then_with(|| b.cmp(a))
    });

    let mut out = Vec::new();
    for (idx, p) in disk_files.into_iter().enumerate() {
        if let Some(sum) = summarize_session_file(idx + 1, &p) {
            out.push(sum);
        }
    }
    out
}

fn summarize_session_file(index: usize, path: &Path) -> Option<SessionSummary> {
    let compact_p = compact_path_for(path);
    let read_target = if compact_p.is_file() { &compact_p } else { path };
    let file_len = fs::metadata(read_target).map(|m| m.len()).unwrap_or(0);

    let mut sid = String::new();
    let mut start_time = String::new();
    let mut last_updated = String::new();
    let mut explicit_summary = String::new();
    let mut first_user_preview = String::new();

    let mut process_line = |line: &str| {
        let Ok(v) = serde_json::from_str::<Value>(line.trim()) else {
            return;
        };
        if let Some(s) = v.get("sessionId").and_then(|x| x.as_str()) {
            sid = s.to_string();
            start_time = v.get("startTime").and_then(|x| x.as_str()).unwrap_or("").to_string();
            last_updated = v.get("lastUpdated").and_then(|x| x.as_str()).unwrap_or(&start_time).to_string();
            if let Some(sum) = v.get("summary").and_then(|x| x.as_str()) {
                if !sum.trim().is_empty() {
                    explicit_summary = sum.trim().to_string();
                }
            }
        }
        if let Some(set_obj) = v.get("$set") {
            if let Some(lu) = set_obj.get("lastUpdated").and_then(|x| x.as_str()) {
                last_updated = lu.to_string();
            }
            if let Some(sum) = set_obj.get("summary").and_then(|x| x.as_str()) {
                if !sum.trim().is_empty() {
                    explicit_summary = sum.trim().to_string();
                }
            }
        }
        if first_user_preview.is_empty() && v.get("type").and_then(|s| s.as_str()) == Some("user") {
            if let Some(arr) = v.get("content").and_then(|c| c.as_array()) {
                for item in arr {
                    if let Some(txt) = item.get("text").and_then(|s| s.as_str()) {
                        if !crate::context::is_ignored_user_content(txt) {
                            first_user_preview = txt.lines().next().unwrap_or("").chars().take(72).collect();
                            break;
                        }
                    }
                }
            }
        }
    };

    if file_len <= 512 * 1024 {
        let file = File::open(read_target).ok()?;
        let reader = BufReader::new(file);
        for line in reader.lines().map_while(Result::ok) {
            process_line(&line);
        }
    } else {
        // Fast head + tail scan for huge legacy files without .compact/
        let mut file = File::open(read_target).ok()?;
        let head_len = (128 * 1024).min(file_len as usize);
        let mut head_buf = vec![0u8; head_len];
        let n = file.read(&mut head_buf).unwrap_or(0);
        let head_str = String::from_utf8_lossy(&head_buf[..n]);
        for line in head_str.lines() {
            process_line(line);
        }
        if file_len > 128 * 1024 {
            let tail_start = file_len.saturating_sub(128 * 1024);
            if file.seek(SeekFrom::Start(tail_start)).is_ok() {
                let mut tail_buf = Vec::new();
                let _ = file.read_to_end(&mut tail_buf);
                let tail_str = String::from_utf8_lossy(&tail_buf);
                for line in tail_str.lines().skip(1) {
                    process_line(line);
                }
            }
        }
    }

    if sid.is_empty() {
        return None;
    }
    let preview = if !explicit_summary.is_empty() {
        explicit_summary
    } else {
        first_user_preview
    };
    Some(SessionSummary {
        index,
        session_id: sid,
        path: path.to_path_buf(),
        start_time,
        last_updated,
        preview,
    })
}

fn find_matching_session(config: &AppConfig, summaries: &[SessionSummary], spec: &str) -> Option<SessionSummary> {
    if spec == "latest" {
        return summaries.first().cloned();
    }
    // Check if spec is an existing file path directly
    let direct_path = Path::new(spec);
    if direct_path.is_file() {
        if let Some(sum) = summarize_session_file(1, direct_path) {
            return Some(sum);
        }
    }

    if let Ok(num) = spec.parse::<usize>() {
        if num >= 1 {
            if let Some(found) = summaries.iter().find(|s| s.index == num) {
                return Some(found.clone());
            }
        }
    }

    let is_match = |sum: &SessionSummary| -> bool {
        if sum.session_id == spec || sum.session_id.starts_with(spec) || spec.starts_with(&sum.session_id) {
            return true;
        }
        let short8: String = sum.session_id.chars().filter(|c| c.is_ascii_hexdigit()).take(8).collect();
        if !short8.is_empty() && (spec.contains(&short8) || short8.starts_with(spec)) {
            return true;
        }
        let path_str = sum.path.to_string_lossy();
        if path_str.contains(spec) {
            return true;
        }
        if let Some(stem) = sum.path.file_stem().and_then(|s| s.to_str()) {
            if stem == spec || stem.contains(spec) || spec.contains(stem) {
                return true;
            }
            if stem.starts_with("session-") && &stem[8..] == spec {
                return true;
            }
        }
        false
    };

    if let Some(found) = summaries.iter().find(|s| is_match(s)) {
        return Some(found.clone());
    }

    // Search all slugs if UUID, filename, or timestamp stem specified across projects
    if let Ok(slugs) = fs::read_dir(&config.paths.history_chats_dir) {
        for slug_entry in slugs.flatten() {
            let sp = slug_entry.path();
            if !sp.is_dir() {
                continue;
            }
            if let Ok(files) = fs::read_dir(sp) {
                for f in files.flatten() {
                    let fp = f.path();
                    if fp.extension().and_then(|s| s.to_str()) == Some("jsonl") {
                        if let Some(sum) = summarize_session_file(1, &fp) {
                            if is_match(&sum) {
                                return Some(sum);
                            }
                        }
                    }
                }
            }
        }
    }
    None
}

pub fn delete_session(config: &AppConfig, spec: &str) -> Result<String, String> {
    let summaries = list_sessions(config);
    let Some(target) = find_matching_session(config, &summaries, spec) else {
        return Err(format!("Session '{}' not found.", spec));
    };
    fs::remove_file(&target.path).map_err(|e| format!("Failed deleting session: {}", e))?;
    let compact_p = compact_path_for(&target.path);
    if compact_p.exists() {
        let _ = fs::remove_file(&compact_p);
    }
    if let Some(db_path) = summary_db_path_for(&target.path) {
        let _ = db_delete_session(&db_path, &target.session_id);
    }
    Ok(target.session_id)
}

fn truncate_chars_with_flag(s: &str, max_chars: usize) -> (String, bool) {
    let mut count = 0usize;
    let mut byte_end = s.len();
    let mut truncated = false;
    for (idx, _) in s.char_indices() {
        if count == max_chars {
            byte_end = idx;
            truncated = true;
            break;
        }
        count += 1;
    }
    if truncated {
        (format!("{}... [truncated]", &s[..byte_end]), true)
    } else {
        (s.to_string(), false)
    }
}

fn compact_tool_args(args: &Value) -> (Value, bool) {
    let Some(obj) = args.as_object() else {
        return (args.clone(), false);
    };
    let mut out = serde_json::Map::new();
    let mut any_trunc = false;
    for (k, v) in obj {
        if let Some(s) = v.as_str() {
            let (trimmed, was_trunc) = truncate_chars_with_flag(s, 240);
            if was_trunc {
                any_trunc = true;
            }
            out.insert(k.clone(), Value::String(trimmed));
        } else if let Some(arr) = v.as_array() {
            if arr.len() > 12 {
                any_trunc = true;
                let mut sub: Vec<Value> = arr.iter().take(12).cloned().collect();
                sub.push(json!(format!("... ({} more items)", arr.len() - 12)));
                out.insert(k.clone(), Value::Array(sub));
            } else {
                out.insert(k.clone(), v.clone());
            }
        } else {
            out.insert(k.clone(), v.clone());
        }
    }
    (Value::Object(out), any_trunc)
}

pub fn compact_record_from_full(rec: &Value) -> Value {
    let Some(obj) = rec.as_object() else {
        return rec.clone();
    };
    let rec_type = obj.get("type").and_then(|v| v.as_str()).unwrap_or("");
    let mut truncated_fields: Vec<String> = Vec::new();

    match rec_type {
        "user" => {
            let mut out = obj.clone();
            if let Some(arr) = obj.get("content").and_then(|v| v.as_array()) {
                let mut new_parts = Vec::with_capacity(arr.len());
                for part in arr {
                    if let Some(fr) = part.get("functionResponse") {
                        let name = fr.get("name").and_then(|v| v.as_str()).unwrap_or("tool");
                        let resp_val = fr.get("response").cloned().unwrap_or(Value::Null);
                        let resp_str = match &resp_val {
                            Value::String(s) => s.clone(),
                            other => serde_json::to_string(other).unwrap_or_default(),
                        };
                        let (preview, was_trunc) = truncate_chars_with_flag(&resp_str, 300);
                        if was_trunc {
                            if !truncated_fields.iter().any(|f| f == "response") {
                                truncated_fields.push("response".to_string());
                            }
                            new_parts.push(json!({
                                "functionResponse": {
                                    "name": name,
                                    "response": {
                                        "preview": preview,
                                        "truncated": true
                                    }
                                }
                            }));
                        } else {
                            new_parts.push(part.clone());
                        }
                    } else if let Some(txt) = part.get("text").and_then(|v| v.as_str()) {
                        let (trimmed, was_trunc) = truncate_chars_with_flag(txt, 8000);
                        if was_trunc && !truncated_fields.iter().any(|f| f == "content") {
                            truncated_fields.push("content".to_string());
                        }
                        new_parts.push(json!({ "text": trimmed }));
                    } else if part.get("inlineData").is_some() {
                        if !truncated_fields.iter().any(|f| f == "inlineData") {
                            truncated_fields.push("inlineData".to_string());
                        }
                        new_parts.push(json!({ "text": "[inline media omitted in compact transcript]" }));
                    } else {
                        new_parts.push(part.clone());
                    }
                }
                out.insert("content".to_string(), Value::Array(new_parts));
            }
            if !truncated_fields.is_empty() {
                out.insert("truncated_fields".to_string(), json!(truncated_fields));
            }
            Value::Object(out)
        }
        "gemini" => {
            let mut out = obj.clone();
            if out.remove("rawParts").is_some() {
                truncated_fields.push("rawParts".to_string());
            }
            if let Some(txt) = obj.get("content").and_then(|v| v.as_str()) {
                let (trimmed, was_trunc) = truncate_chars_with_flag(txt, 16000);
                if was_trunc {
                    truncated_fields.push("content".to_string());
                    out.insert("content".to_string(), Value::String(trimmed));
                }
            }
            if let Some(thoughts) = obj.get("thoughts").and_then(|v| v.as_array()) {
                let mut compact_thoughts = Vec::new();
                let mut th_trunc = thoughts.len() > 8;
                for th in thoughts.iter().take(8) {
                    let subj = th.get("subject").and_then(|v| v.as_str()).unwrap_or("");
                    let desc = th.get("description").and_then(|v| v.as_str()).unwrap_or("");
                    let (trimmed_desc, was_trunc) = truncate_chars_with_flag(desc, 600);
                    if was_trunc {
                        th_trunc = true;
                    }
                    compact_thoughts.push(json!({
                        "subject": subj,
                        "description": trimmed_desc
                    }));
                }
                if th_trunc {
                    truncated_fields.push("thoughts".to_string());
                }
                out.insert("thoughts".to_string(), Value::Array(compact_thoughts));
            }
            if let Some(tcs) = obj.get("toolCalls").and_then(|v| v.as_array()) {
                let mut compact_tcs = Vec::with_capacity(tcs.len());
                let mut tc_trunc = false;
                for tc in tcs {
                    let mut tc_obj = tc.as_object().cloned().unwrap_or_default();
                    if let Some(args) = tc_obj.get("args").cloned() {
                        let (c_args, was_trunc) = compact_tool_args(&args);
                        if was_trunc {
                            tc_trunc = true;
                        }
                        tc_obj.insert("args".to_string(), c_args);
                    }
                    if let Some(rd) = tc_obj.get("resultDisplay").and_then(|v| v.as_str()) {
                        let (c_rd, was_trunc) = truncate_chars_with_flag(rd, 240);
                        if was_trunc {
                            tc_trunc = true;
                        }
                        tc_obj.insert("resultDisplay".to_string(), Value::String(c_rd));
                    }
                    compact_tcs.push(Value::Object(tc_obj));
                }
                if tc_trunc {
                    truncated_fields.push("toolCalls.args".to_string());
                }
                out.insert("toolCalls".to_string(), Value::Array(compact_tcs));
            }
            if !truncated_fields.is_empty() {
                out.insert("truncated_fields".to_string(), json!(truncated_fields));
            }
            Value::Object(out)
        }
        "compression_snapshot" => {
            let mut out = obj.clone();
            if out.remove("preservedTail").is_some() {
                truncated_fields.push("preservedTail".to_string());
            }
            if let Some(snap) = obj.get("snapshot").and_then(|v| v.as_str()) {
                let (trimmed, was_trunc) = truncate_chars_with_flag(snap, 600);
                if was_trunc {
                    truncated_fields.push("snapshot".to_string());
                    out.insert("snapshot".to_string(), Value::String(trimmed));
                }
            }
            if !truncated_fields.is_empty() {
                out.insert("truncated_fields".to_string(), json!(truncated_fields));
            }
            Value::Object(out)
        }
        _ => rec.clone(),
    }
}

pub fn backfill_compact_transcript(full_path: &Path, compact_path: &Path) -> Result<(), String> {
    let file = File::open(full_path).map_err(|e| format!("Open full session error: {}", e))?;
    if let Some(parent) = compact_path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    let tmp_path = compact_path.with_extension("jsonl.tmp");
    let mut out = OpenOptions::new()
        .create(true)
        .write(true)
        .truncate(true)
        .open(&tmp_path)
        .map_err(|e| format!("Create compact tmp error: {}", e))?;

    let reader = BufReader::new(file);
    for line in reader.lines().map_while(Result::ok) {
        let t = line.trim();
        if t.is_empty() {
            continue;
        }
        if let Ok(v) = serde_json::from_str::<Value>(t) {
            let compact = compact_record_from_full(&v);
            if let Ok(s) = serde_json::to_string(&compact) {
                let _ = writeln!(out, "{}", s);
            }
        }
    }
    let _ = out.flush();
    fs::rename(&tmp_path, compact_path).map_err(|e| format!("Rename compact transcript error: {}", e))?;
    Ok(())
}

#[derive(Debug, Clone)]
struct DbSessionRow {
    session_id: String,
    file_path: String,
    start_time: String,
    last_updated: String,
    preview: String,
    file_size: i64,
}

fn init_summary_db(db_path: &Path) -> Result<Connection, String> {
    if let Some(parent) = db_path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    let conn = Connection::open(db_path).map_err(|e| format!("SQLite open error: {}", e))?;
    let _ = conn.execute_batch(
        "PRAGMA journal_mode=WAL;
         PRAGMA synchronous=NORMAL;
         PRAGMA busy_timeout=2000;
         CREATE TABLE IF NOT EXISTS session_summaries (
             session_id TEXT PRIMARY KEY,
             slug TEXT NOT NULL,
             file_path TEXT NOT NULL,
             compact_path TEXT NOT NULL,
             title TEXT NOT NULL,
             preview TEXT NOT NULL,
             start_time TEXT NOT NULL,
             last_updated TEXT NOT NULL,
             turn_count INTEGER NOT NULL DEFAULT 0,
             has_error INTEGER NOT NULL DEFAULT 0,
             file_size INTEGER NOT NULL DEFAULT 0
         );
         CREATE INDEX IF NOT EXISTS idx_session_summaries_slug_updated
             ON session_summaries(slug, last_updated DESC);",
    );
    let _ = conn.execute_batch(
        "CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
             session_id UNINDEXED,
             title,
             preview
         );",
    );
    Ok(conn)
}

#[allow(clippy::too_many_arguments)]
fn db_upsert_session(
    db_path: &Path,
    session_id: &str,
    slug: &str,
    file_path: &Path,
    compact_path: &Path,
    title: &str,
    preview: &str,
    start_time: &str,
    last_updated: &str,
    turn_count: i64,
    has_error: bool,
    file_size: i64,
) -> Result<(), String> {
    let conn = init_summary_db(db_path)?;
    let fp_str = file_path.to_string_lossy().to_string();
    let cp_str = compact_path.to_string_lossy().to_string();
    conn.execute(
        "INSERT INTO session_summaries (
             session_id, slug, file_path, compact_path, title, preview,
             start_time, last_updated, turn_count, has_error, file_size
         ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)
         ON CONFLICT(session_id) DO UPDATE SET
             slug = excluded.slug,
             file_path = excluded.file_path,
             compact_path = excluded.compact_path,
             title = CASE WHEN excluded.title != '' AND excluded.title != 'New Session' THEN excluded.title ELSE session_summaries.title END,
             preview = CASE WHEN excluded.preview != '' AND excluded.preview != 'New Session' THEN excluded.preview ELSE session_summaries.preview END,
             last_updated = excluded.last_updated,
             turn_count = MAX(session_summaries.turn_count, excluded.turn_count),
             has_error = MAX(session_summaries.has_error, excluded.has_error),
             file_size = excluded.file_size",
        params![
            session_id,
            slug,
            fp_str,
            cp_str,
            title,
            preview,
            start_time,
            last_updated,
            turn_count,
            if has_error { 1i64 } else { 0i64 },
            file_size
        ],
    )
    .map_err(|e| format!("SQLite upsert error: {}", e))?;
    let _ = conn.execute("DELETE FROM sessions_fts WHERE session_id = ?1", params![session_id]);
    let _ = conn.execute(
        "INSERT INTO sessions_fts (session_id, title, preview) VALUES (?1, ?2, ?3)",
        params![session_id, title, preview],
    );
    Ok(())
}

#[allow(clippy::too_many_arguments)]
fn db_record_user_prompt(
    db_path: &Path,
    session_id: &str,
    slug: &str,
    file_path: &Path,
    compact_path: &Path,
    preview: &str,
    ts: &str,
    file_size: i64,
) -> Result<(), String> {
    let conn = init_summary_db(db_path)?;
    let fp_str = file_path.to_string_lossy().to_string();
    let cp_str = compact_path.to_string_lossy().to_string();
    let title = if preview.is_empty() { "New Session" } else { preview };
    conn.execute(
        "INSERT INTO session_summaries (
             session_id, slug, file_path, compact_path, title, preview,
             start_time, last_updated, turn_count, has_error, file_size
         ) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?7, 1, 0, ?8)
         ON CONFLICT(session_id) DO UPDATE SET
             title = CASE WHEN session_summaries.title = '' OR session_summaries.title = 'New Session' THEN excluded.title ELSE session_summaries.title END,
             preview = CASE WHEN session_summaries.preview = '' OR session_summaries.preview = 'New Session' THEN excluded.preview ELSE session_summaries.preview END,
             last_updated = excluded.last_updated,
             turn_count = session_summaries.turn_count + 1,
             file_size = excluded.file_size",
        params![session_id, slug, fp_str, cp_str, title, title, ts, file_size],
    )
    .map_err(|e| format!("SQLite user prompt update error: {}", e))?;
    let _ = conn.execute("DELETE FROM sessions_fts WHERE session_id = ?1", params![session_id]);
    let _ = conn.execute(
        "INSERT INTO sessions_fts (session_id, title, preview)
         SELECT session_id, title, preview FROM session_summaries WHERE session_id = ?1",
        params![session_id],
    );
    Ok(())
}

#[allow(clippy::too_many_arguments)]
fn db_record_model_turn(
    db_path: &Path,
    session_id: &str,
    slug: &str,
    file_path: &Path,
    compact_path: &Path,
    ts: &str,
    has_error: bool,
    file_size: i64,
) -> Result<(), String> {
    let conn = init_summary_db(db_path)?;
    let fp_str = file_path.to_string_lossy().to_string();
    let cp_str = compact_path.to_string_lossy().to_string();
    conn.execute(
        "INSERT INTO session_summaries (
             session_id, slug, file_path, compact_path, title, preview,
             start_time, last_updated, turn_count, has_error, file_size
         ) VALUES (?1, ?2, ?3, ?4, 'New Session', 'New Session', ?5, ?5, 1, ?6, ?7)
         ON CONFLICT(session_id) DO UPDATE SET
             last_updated = excluded.last_updated,
             turn_count = session_summaries.turn_count + 1,
             has_error = MAX(session_summaries.has_error, excluded.has_error),
             file_size = excluded.file_size",
        params![
            session_id,
            slug,
            fp_str,
            cp_str,
            ts,
            if has_error { 1i64 } else { 0i64 },
            file_size
        ],
    )
    .map_err(|e| format!("SQLite model turn update error: {}", e))?;
    Ok(())
}

fn db_update_summary_title(db_path: &Path, session_id: &str, summary: &str) -> Result<(), String> {
    let conn = init_summary_db(db_path)?;
    conn.execute(
        "UPDATE session_summaries SET title = ?2, preview = ?2 WHERE session_id = ?1",
        params![session_id, summary],
    )
    .map_err(|e| format!("SQLite summary title update error: {}", e))?;
    let _ = conn.execute("DELETE FROM sessions_fts WHERE session_id = ?1", params![session_id]);
    let _ = conn.execute(
        "INSERT INTO sessions_fts (session_id, title, preview) VALUES (?1, ?2, ?2)",
        params![session_id, summary],
    );
    Ok(())
}

fn db_touch_updated(db_path: &Path, session_id: &str, ts: &str, file_size: i64) -> Result<(), String> {
    let conn = init_summary_db(db_path)?;
    conn.execute(
        "UPDATE session_summaries SET last_updated = ?2, file_size = ?3 WHERE session_id = ?1",
        params![session_id, ts, file_size],
    )
    .map_err(|e| format!("SQLite touch_updated error: {}", e))?;
    Ok(())
}

fn db_delete_session(db_path: &Path, session_id: &str) -> Result<(), String> {
    if !db_path.exists() {
        return Ok(());
    }
    let conn = init_summary_db(db_path)?;
    let _ = conn.execute("DELETE FROM session_summaries WHERE session_id = ?1", params![session_id]);
    let _ = conn.execute("DELETE FROM sessions_fts WHERE session_id = ?1", params![session_id]);
    Ok(())
}

fn db_list_sessions_for_slug(db_path: &Path, slug: &str) -> Result<Vec<DbSessionRow>, String> {
    if !db_path.exists() {
        return Ok(Vec::new());
    }
    let conn = init_summary_db(db_path)?;
    let mut stmt = conn
        .prepare(
            "SELECT session_id, file_path, start_time, last_updated, preview, file_size
             FROM session_summaries
             WHERE slug = ?1
             ORDER BY last_updated DESC",
        )
        .map_err(|e| format!("SQLite prepare error: {}", e))?;
    let rows = stmt
        .query_map(params![slug], |row| {
            Ok(DbSessionRow {
                session_id: row.get(0)?,
                file_path: row.get(1)?,
                start_time: row.get(2)?,
                last_updated: row.get(3)?,
                preview: row.get(4)?,
                file_size: row.get(5)?,
            })
        })
        .map_err(|e| format!("SQLite query error: {}", e))?;
    let mut out = Vec::new();
    for r in rows.flatten() {
        out.push(r);
    }
    Ok(out)
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum LoopVerdict {
    Ok,
    Warn(String),
    HardStop(String),
}

#[derive(Debug, Default)]
pub struct LoopDetector {
    recent_calls: VecDeque<String>,
    recent_semantic: VecDeque<String>,
    counts: HashMap<String, usize>,
    semantic_counts: HashMap<String, usize>,
    consecutive_errors: usize,
    last_text_chunk: String,
    repeated_chunk_count: usize,
    pub tool_threshold: usize,
    pub content_threshold: usize,
}

impl LoopDetector {
    pub fn new(tool_threshold: usize, content_threshold: usize) -> Self {
        Self {
            tool_threshold: tool_threshold.max(2),
            content_threshold: content_threshold.max(3),
            ..Default::default()
        }
    }

    fn build_semantic_signature(name: &str, args: &Value) -> String {
        let obj = match args.as_object() {
            Some(o) => o,
            None => return format!("{}:{}", name, args),
        };
        match name {
            "read_file" | "view_file" => {
                let path = obj
                    .get("file_path")
                    .or_else(|| obj.get("path"))
                    .or_else(|| obj.get("TargetFile"))
                    .or_else(|| obj.get("AbsolutePath"))
                    .and_then(|v| v.as_str())
                    .unwrap_or("");
                let start = obj
                    .get("start_line")
                    .or_else(|| obj.get("StartLine"))
                    .and_then(|v| v.as_i64())
                    .unwrap_or(0);
                let end = obj
                    .get("end_line")
                    .or_else(|| obj.get("EndLine"))
                    .and_then(|v| v.as_i64())
                    .unwrap_or(0);
                let offset = obj
                    .get("ContentOffset")
                    .or_else(|| obj.get("offset"))
                    .and_then(|v| v.as_i64())
                    .unwrap_or(0);
                format!("{}:{}:{}-{}:{}", name, path, start, end, offset)
            }
            "grep_search" => {
                let path = obj
                    .get("path")
                    .or_else(|| obj.get("TargetDirectory"))
                    .and_then(|v| v.as_str())
                    .unwrap_or("");
                let pat = obj
                    .get("pattern")
                    .or_else(|| obj.get("query"))
                    .and_then(|v| v.as_str())
                    .unwrap_or("");
                format!("{}:{}:{}", name, path, pat)
            }
            "run_shell_command" | "run_command" => {
                let cmd = obj
                    .get("command")
                    .or_else(|| obj.get("CommandLine"))
                    .and_then(|v| v.as_str())
                    .unwrap_or("");
                let head: String = cmd.split_whitespace().take(4).collect::<Vec<_>>().join(" ");
                format!("{}:{}", name, head)
            }
            _ => {
                let mut norm = args.clone();
                if let Some(m) = norm.as_object_mut() {
                    m.remove("reason");
                    m.remove("keywords");
                    m.remove("goal");
                    m.remove("toolAction");
                    m.remove("toolSummary");
                }
                format!("{}:{}", name, norm)
            }
        }
    }

    fn detect_oscillation(seq: &VecDeque<String>) -> Option<usize> {
        let len = seq.len();
        if len >= 4 {
            let a1 = &seq[len - 4];
            let b1 = &seq[len - 3];
            let a2 = &seq[len - 2];
            let b2 = &seq[len - 1];
            if a1 == a2 && b1 == b2 && a1 != b1 {
                return Some(2);
            }
        }
        if len >= 6 {
            if seq[len - 6] == seq[len - 3]
                && seq[len - 5] == seq[len - 2]
                && seq[len - 4] == seq[len - 1]
            {
                return Some(3);
            }
        }
        None
    }

    pub fn check_tool_call(&mut self, name: &str, args: &Value) -> LoopVerdict {
        let mut norm = args.clone();
        if let Some(obj) = norm.as_object_mut() {
            obj.remove("reason");
            obj.remove("keywords");
            obj.remove("goal");
            obj.remove("toolAction");
            obj.remove("toolSummary");
        }
        let sig = format!("{}:{}", name, norm);
        let c = self.counts.entry(sig.clone()).or_insert(0);
        *c += 1;
        let exact_count = *c;
        self.recent_calls.push_back(sig);
        if self.recent_calls.len() > 24 {
            if let Some(old) = self.recent_calls.pop_front() {
                if let Some(cnt) = self.counts.get_mut(&old) {
                    *cnt = cnt.saturating_sub(1);
                }
            }
        }

        let sem_sig = Self::build_semantic_signature(name, args);
        let sc = self.semantic_counts.entry(sem_sig.clone()).or_insert(0);
        *sc += 1;
        let sem_count = *sc;
        self.recent_semantic.push_back(sem_sig);
        if self.recent_semantic.len() > 24 {
            if let Some(old) = self.recent_semantic.pop_front() {
                if let Some(cnt) = self.semantic_counts.get_mut(&old) {
                    *cnt = cnt.saturating_sub(1);
                }
            }
        }

        // Antigravity-grade Interception: Never kill process on loop; block redundant call & guide model
        if exact_count >= self.tool_threshold + 2 {
            return LoopVerdict::HardStop(format!(
                "Loop Guard Intervention: Identical tool call `{}` with identical parameters was repeated {} times. Redundant execution blocked. You now have the necessary context. Do NOT call this tool again with identical parameters. Proceed to take action (edit/command) or deliver your complete answer to the user.",
                name, exact_count
            ));
        }
        if exact_count >= self.tool_threshold {
            return LoopVerdict::Warn(format!(
                "Loop Guard Advisory: Tool call `{}` has been repeated {} times with identical parameters. Synthesize your findings or proceed to editing/executing.",
                name, exact_count
            ));
        }
        if sem_count >= self.tool_threshold + 4 {
            return LoopVerdict::HardStop(format!(
                "Loop Guard Intervention: Repetitive pattern detected on `{}` ({} similar calls in recent window). Call blocked. Do not repeat this pattern. Proceed to the next substantive step or present your conclusions.",
                name, sem_count
            ));
        }
        if let Some(period) = Self::detect_oscillation(&self.recent_semantic) {
            return LoopVerdict::Warn(format!(
                "Oscillation loop detected ({}-step cycle ending at `{}`). Break the cycle and try a different approach.",
                period, name
            ));
        }
        LoopVerdict::Ok
    }

    pub fn record_tool_outcome(&mut self, is_err: bool) -> LoopVerdict {
        if is_err {
            self.consecutive_errors += 1;
            if self.consecutive_errors >= 6 {
                return LoopVerdict::Warn(format!(
                    "{} consecutive tool failures. Stop repeating failing actions. Reassess your approach or report your blocker to the user.",
                    self.consecutive_errors
                ));
            }
            if self.consecutive_errors >= 4 {
                return LoopVerdict::Warn(format!(
                    "{} consecutive tool failures. Reassess assumptions before retrying.",
                    self.consecutive_errors
                ));
            }
        } else {
            self.consecutive_errors = 0;
        }
        LoopVerdict::Ok
    }

    pub fn record_text_delta(&mut self, chunk: &str) -> bool {
        let trimmed = chunk.trim();
        if trimmed.len() < 12 {
            return false;
        }
        if trimmed == self.last_text_chunk {
            self.repeated_chunk_count += 1;
        } else {
            self.last_text_chunk = trimmed.to_string();
            self.repeated_chunk_count = 1;
        }
        self.repeated_chunk_count >= self.content_threshold
    }
}

/// Expands `@path/to/file` mentions in user prompts into inline text or base64 multimodal blobs.
pub fn build_user_parts_with_attachments(config: &AppConfig, prompt: &str) -> Vec<ContentPart> {
    let mut parts = vec![ContentPart::text(prompt.to_string())];
    let mut extra_notes = Vec::new();
    let mut seen = std::collections::HashSet::new();

    for token in prompt.split_whitespace() {
        let Some(raw_ref) = token.strip_prefix('@') else {
            continue;
        };
        let clean = raw_ref.trim_matches(|c: char| matches!(c, ',' | ';' | ')' | ']' | '"' | '\''));
        if clean.is_empty() {
            continue;
        }
        let candidate = if let Some(rest) = clean.strip_prefix("~/") {
            config.paths.home_dir.join(rest)
        } else {
            let p = Path::new(clean);
            if p.is_absolute() {
                p.to_path_buf()
            } else {
                config.cwd.join(p)
            }
        };
        if !candidate.is_file() || !seen.insert(candidate.clone()) {
            continue;
        }
        let ext = candidate
            .extension()
            .and_then(|s| s.to_str())
            .unwrap_or("")
            .to_ascii_lowercase();
        let mime = match ext.as_str() {
            "png" => Some("image/png"),
            "jpg" | "jpeg" => Some("image/jpeg"),
            "webp" => Some("image/webp"),
            "gif" => Some("image/gif"),
            "pdf" => Some("application/pdf"),
            "wav" => Some("audio/wav"),
            "mp3" => Some("audio/mp3"),
            _ => None,
        };
        if let Some(m) = mime {
            if let Ok(bytes) = fs::read(&candidate) {
                if bytes.len() <= 16 * 1024 * 1024 {
                    parts.push(ContentPart::inline_data(m, B64.encode(bytes)));
                    extra_notes.push(format!("[Attached multimodal file @{} ({})]", clean, m));
                }
            }
        } else if let Ok(txt) = fs::read_to_string(&candidate) {
            let sliced: String = txt.chars().take(32_000).collect();
            extra_notes.push(format!(
                "<attached_file path=\"{}\">\n{}\n</attached_file>",
                candidate.display(),
                sliced
            ));
        }
    }

    if !extra_notes.is_empty() {
        parts.push(ContentPart::text(extra_notes.join("\n\n")));
    }
    parts
}

fn simple_sha_hex(input: &str) -> String {
    // Deterministic FNV-1a 256-bit style hex tag without extra crypto crate dependency
    let mut h1: u64 = 0xcbf29ce484222325;
    let mut h2: u64 = 0x84222325cbf29ce4;
    for &b in input.as_bytes() {
        h1 ^= b as u64;
        h1 = h1.wrapping_mul(0x100000001b3);
        h2 ^= (b as u64).wrapping_add(17);
        h2 = h2.wrapping_mul(0x100000001b3);
    }
    format!("{:016x}{:016x}", h1, h2)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dual_lossless_and_compression_snapshot_replay_works() {
        let tmp_dir = std::env::temp_dir().join(format!("mrflow_sess_dir_{}", Uuid::new_v4()));
        let slug_dir = tmp_dir.join("test");
        let _ = fs::create_dir_all(&slug_dir);
        let tmp_path = slug_dir.join("session-test.jsonl");
        let compact_path = compact_path_for(&tmp_path);
        let db_path = tmp_dir.join("session_summaries.db");
        let vault = SessionVault {
            session_id: "test-sid-1234".to_string(),
            slug: "test".to_string(),
            path: tmp_path.clone(),
            compact_path: compact_path.clone(),
            summary_db_path: Some(db_path.clone()),
            project_hash: "0000".to_string(),
        };
        append_json_line(
            &tmp_path,
            &json!({ "sessionId": "test-sid-1234", "startTime": "2026-11-11T00:00:00Z", "lastUpdated": "2026-11-11T00:00:00Z", "kind": "main" }),
        )
        .unwrap();
        append_json_line(
            &compact_path,
            &json!({ "sessionId": "test-sid-1234", "startTime": "2026-11-11T00:00:00Z", "lastUpdated": "2026-11-11T00:00:00Z", "kind": "main" }),
        )
        .unwrap();

        vault.append_user_prompt("first prompt").unwrap();
        vault
            .append_model_turn(
                "gemini-3.8-flash-high",
                "first answer",
                &[],
                &TokenUsage::default(),
                &[],
                &[ContentPart::text("first "), ContentPart::text("answer")],
            )
            .unwrap();
        vault.append_user_prompt("second prompt").unwrap();
        vault
            .append_model_turn(
                "gemini-3.8-flash-high",
                "second answer",
                &[],
                &TokenUsage::default(),
                &[],
                &[ContentPart::text("second answer")],
            )
            .unwrap();

        let tail = vec![ChatMessage {
            role: "user".to_string(),
            parts: vec![ContentPart::text("preserved tail question")],
        }];
        vault
            .append_compression_snapshot("<state_snapshot>compact state</state_snapshot>", &tail, 5000, 300)
            .unwrap();
        vault.append_user_prompt("third prompt").unwrap();
        vault.append_summary("Dual snapshot & rewind test").unwrap();

        // Full lossless lines remain in file ("versi utuh")
        let raw_content = fs::read_to_string(&tmp_path).unwrap();
        assert!(raw_content.contains("first prompt"));
        assert!(raw_content.contains("second prompt"));

        // Resume reconstructs compact anchor + tail + subsequent prompt ("yang diringkas")
        let (sid, resumed) = load_jsonl_session(&tmp_path).unwrap();
        assert_eq!(sid, "test-sid-1234");
        assert_eq!(resumed.len(), 4);
        assert!(resumed[0].parts[0].text.as_deref().unwrap().contains("<state_snapshot>compact state</state_snapshot>"));
        assert_eq!(resumed[2].parts[0].text.as_deref(), Some("preserved tail question"));
        assert_eq!(resumed[3].parts[0].text.as_deref(), Some("third prompt"));

        // Rewind to keep_count=3 drops "third prompt" while retaining lossless history on disk
        vault.append_rewind(3).unwrap();
        let (_, rewound) = load_jsonl_session(&tmp_path).unwrap();
        assert_eq!(rewound.len(), 3);

        // Explicit summary appears in summarize_session_file
        let summary = summarize_session_file(1, &tmp_path).unwrap();
        assert_eq!(summary.preview, "Dual snapshot & rewind test");

        let _ = fs::remove_file(&tmp_path);
    }

    #[test]
    fn loop_detector_allows_pagination_and_blocks_identical() {
        let mut detector = LoopDetector::new(3, 3);
        // Slicing different pages of the same file is legitimate work, not a loop!
        for i in 0..10 {
            let start = i * 100 + 1;
            let end = (i + 1) * 100;
            let args = json!({
                "AbsolutePath": "/opt/floworkos/bin/flowork-neural-conduit",
                "StartLine": start,
                "EndLine": end
            });
            let verdict = detector.check_tool_call("view_file", &args);
            assert_eq!(verdict, LoopVerdict::Ok);
        }

        // Repeating identical slice 3 times warns, 5 times interventions
        let identical_args = json!({
            "AbsolutePath": "/opt/floworkos/bin/flowork-neural-conduit",
            "StartLine": 1,
            "EndLine": 100
        });
        // 2nd call (first was in loop above)
        assert_eq!(detector.check_tool_call("view_file", &identical_args), LoopVerdict::Ok);
        // 3rd call triggers Warn advisory
        let v3 = detector.check_tool_call("view_file", &identical_args);
        assert!(matches!(v3, LoopVerdict::Warn(_)));
    }

    #[test]
    fn dual_compact_transcript_and_sqlite_summary_index_work() {
        let tmp_dir = std::env::temp_dir().join(format!("mrflow_dual_test_{}", Uuid::new_v4()));
        let slug_dir = tmp_dir.join("proj-alpha");
        fs::create_dir_all(&slug_dir).unwrap();
        let full_path = slug_dir.join("session-2026-11-27T10-00-abcd1234.jsonl");
        let compact_path = compact_path_for(&full_path);
        let db_path = tmp_dir.join("session_summaries.db");

        let vault = SessionVault {
            session_id: "abcd1234-0000-0000-0000-000000000001".to_string(),
            slug: "proj-alpha".to_string(),
            path: full_path.clone(),
            compact_path: compact_path.clone(),
            summary_db_path: Some(db_path.clone()),
            project_hash: "hash123".to_string(),
        };

        let header = json!({
            "sessionId": vault.session_id,
            "projectHash": "hash123",
            "startTime": "2026-11-27T10:00:00.000Z",
            "lastUpdated": "2026-11-27T10:00:00.000Z",
            "kind": "main"
        });
        append_json_line(&full_path, &header).unwrap();
        append_json_line(&compact_path, &header).unwrap();

        vault.append_user_prompt("Tolong refactor session vault").unwrap();

        let huge_arg = "X".repeat(2000);
        let huge_resp = "Y".repeat(2000);
        vault
            .append_model_turn(
                "gemini-3.8-flash-high",
                "Siap, gue cek dulu.",
                &["Thinking step 1".to_string()],
                &TokenUsage::default(),
                &[json!({
                    "id": "tc1",
                    "name": "write_file",
                    "status": "ok",
                    "args": { "file_path": "/tmp/a.txt", "content": huge_arg }
                })],
                &[ContentPart::text("Siap, gue cek dulu.")],
            )
            .unwrap();

        vault
            .append_tool_responses(&[ContentPart::function_response(
                "tc1",
                "write_file",
                json!({ "output": huge_resp }),
            )])
            .unwrap();

        vault
            .append_compression_snapshot("Snapshot ringkas", &[], 50000, 4000)
            .unwrap();

        // Verify compact file exists, is much smaller, strips rawParts & preservedTail, and marks truncated_fields
        assert!(compact_path.is_file());
        let full_size = fs::metadata(&full_path).unwrap().len();
        let compact_size = fs::metadata(&compact_path).unwrap().len();
        assert!(compact_size < full_size);

        let compact_text = fs::read_to_string(&compact_path).unwrap();
        assert!(!compact_text.contains("\"rawParts\":"));
        assert!(!compact_text.contains("\"preservedTail\":"));
        assert!(compact_text.contains("\"truncated_fields\""));

        // Verify SQLite summary index has the session
        let rows = db_list_sessions_for_slug(&db_path, "proj-alpha").unwrap();
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0].session_id, vault.session_id);
        assert!(rows[0].preview.contains("Tolong refactor session vault"));

        let _ = fs::remove_dir_all(&tmp_dir);
    }
}
