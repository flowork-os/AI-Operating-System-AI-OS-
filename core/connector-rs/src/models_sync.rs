use chrono::Utc;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::{json, Map, Value};
use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::Path;
use std::time::Duration;
use tokio::sync::{Mutex, RwLock};

use crate::config::ConfigManager;
use crate::vault::{now_ms, VaultManager};

const DEFAULT_AGENT_UA: &str = "antigravity/2.35.0 linux/amd64";
const CATALOG_TTL_MS: i64 = 5 * 60 * 1000;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct LiveModelInfo {
    pub id: String,
    pub display_name: String,
    pub owned_by: String,
    pub tag_title: Option<String>,
    pub tag_description: Option<String>,
    pub recommended: bool,
    pub disabled: bool,
    pub is_internal: bool,
    pub beta: bool,
    pub beta_warning_message: Option<String>,
    pub supports_images: bool,
    pub supports_thinking: bool,
    pub thinking_budget: Option<i64>,
    pub min_thinking_budget: Option<i64>,
    pub max_tokens: u64,
    pub max_output_tokens: u64,
    pub remaining_fraction: Option<f64>,
    pub reset_time: Option<String>,
    pub unavailable: bool,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ModelSortGroup {
    pub display_name: String,
    pub model_ids: Vec<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize, Default)]
pub struct LiveCatalogState {
    pub fetched_at_ms: i64,
    pub source: String,
    pub project_id: String,
    pub default_agent_model_id: String,
    pub active_model: String,
    pub models: Vec<LiveModelInfo>,
    pub deprecated_model_ids: HashMap<String, String>,
    pub sorts: Vec<ModelSortGroup>,
    #[serde(default)]
    pub internal_models: Vec<LiveModelInfo>,
    #[serde(default)]
    pub grouped_models: Value,
    #[serde(default)]
    pub raw_top_keys: Vec<String>,
    #[serde(default)]
    pub load_code_assist_summary: Value,
    pub last_error: Option<String>,
}

pub struct ModelsSyncManager {
    cache: RwLock<LiveCatalogState>,
    sync_lock: Mutex<()>,
}

pub fn effective_cloudcode_user_agent(configured: &str) -> String {
    let trimmed = configured.trim();
    if trimmed.is_empty() || trimmed == "antigravity/2.8.1" {
        DEFAULT_AGENT_UA.to_string()
    } else {
        trimmed.to_string()
    }
}

fn json_field<'a>(obj: &'a Map<String, Value>, camel: &str, snake: &str) -> Option<&'a Value> {
    obj.get(camel).or_else(|| obj.get(snake))
}

fn infer_owned_by(id: &str, display_name: &str, obj: &Map<String, Value>) -> String {
    let mp = json_field(obj, "modelProvider", "model_provider")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_ascii_lowercase();
    let lower = format!("{} {}", id.to_ascii_lowercase(), display_name.to_ascii_lowercase());
    if mp.contains("anthropic") || lower.contains("claude") {
        "anthropic".to_string()
    } else if mp.contains("openai") || lower.contains("gpt") {
        "openai".to_string()
    } else {
        "google".to_string()
    }
}

pub fn parse_fetch_available_models_response(
    raw: &Value,
    project_id: &str,
    current_default: &str,
) -> Option<LiveCatalogState> {
    let root = raw.as_object()?;
    let models_map = json_field(root, "models", "models").and_then(|v| v.as_object())?;

    let default_agent_model_id = json_field(root, "defaultAgentModelId", "default_agent_model_id")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .trim()
        .to_string();

    let mut deprecated_model_ids = HashMap::new();
    if let Some(dep_obj) = json_field(root, "deprecatedModelIds", "deprecated_model_ids")
        .and_then(|v| v.as_object())
    {
        for (old_id, info) in dep_obj {
            if let Some(iobj) = info.as_object() {
                if let Some(new_id) = json_field(iobj, "newModelId", "new_model_id")
                    .and_then(|v| v.as_str())
                    .map(|s| s.trim().to_string())
                    .filter(|s| !s.is_empty())
                {
                    deprecated_model_ids.insert(old_id.clone(), new_id);
                }
            } else if let Some(new_id) = info.as_str().map(|s| s.trim().to_string()).filter(|s| !s.is_empty()) {
                deprecated_model_ids.insert(old_id.clone(), new_id);
            }
        }
    }

    let mut sorts = Vec::new();
    let mut ordered_ids = Vec::new();
    let mut seen_ordered = HashSet::new();

    if let Some(sorts_arr) = json_field(root, "agentModelSorts", "agent_model_sorts")
        .and_then(|v| v.as_array())
    {
        for sort_entry in sorts_arr {
            let Some(sobj) = sort_entry.as_object() else { continue };
            let Some(groups) = json_field(sobj, "groups", "groups").and_then(|v| v.as_array()) else {
                continue;
            };
            for g in groups {
                let Some(gobj) = g.as_object() else { continue };
                let g_name = json_field(gobj, "displayName", "display_name")
                    .and_then(|v| v.as_str())
                    .unwrap_or("")
                    .to_string();
                let ids: Vec<String> = json_field(gobj, "modelIds", "model_ids")
                    .and_then(|v| v.as_array())
                    .map(|arr| {
                        arr.iter()
                            .filter_map(|x| x.as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_default();
                for id in &ids {
                    if seen_ordered.insert(id.clone()) {
                        ordered_ids.push(id.clone());
                    }
                }
                if !ids.is_empty() {
                    sorts.push(ModelSortGroup {
                        display_name: g_name,
                        model_ids: ids,
                    });
                }
            }
        }
    }

    let mut remaining_ids: Vec<String> = models_map
        .keys()
        .filter(|id| !seen_ordered.contains(*id))
        .cloned()
        .collect();
    remaining_ids.sort();
    ordered_ids.extend(remaining_ids);

    let raw_top_keys: Vec<String> = root.keys().cloned().collect();
    let mut grouped_models = json_field(root, "groupedModels", "grouped_models")
        .cloned()
        .unwrap_or_else(|| json!({}));

    if !grouped_models.is_object() {
        grouped_models = json!({});
    }
    if let Some(gobj) = grouped_models.as_object_mut() {
        if !gobj.contains_key("gemini-4-hydrogen") {
            gobj.insert("gemini-4-hydrogen".to_string(), json!({
                "displayName": "Gemini 4 Hydrogen",
                "supportedThinkingLevels": [
                    { "thinkingSuffix": "low", "thinkingDisplayName": "Low" },
                    { "thinkingSuffix": "medium", "thinkingDisplayName": "Medium" },
                    { "thinkingSuffix": "high", "thinkingDisplayName": "XHigh" }
                ]
            }));
        }
        if !gobj.contains_key("gemini-3.8-flash") {
            gobj.insert("gemini-3.8-flash".to_string(), json!({
                "displayName": "Gemini 3.8 Flash",
                "supportedThinkingLevels": [
                    { "thinkingSuffix": "low", "thinkingDisplayName": "Low" },
                    { "thinkingSuffix": "medium", "thinkingDisplayName": "Medium" },
                    { "thinkingSuffix": "high", "thinkingDisplayName": "High" }
                ]
            }));
        }
    }

    let mut models = Vec::new();
    let mut internal_models = Vec::new();
    for id in ordered_ids {
        let Some(details_val) = models_map.get(&id) else { continue };
        let Some(dobj) = details_val.as_object() else { continue };

        let is_internal = json_field(dobj, "isInternal", "is_internal")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);

        let display_name = json_field(dobj, "displayName", "display_name")
            .and_then(|v| v.as_str())
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .unwrap_or_else(|| id.clone());

        let tag_title = json_field(dobj, "tagTitle", "tag_title")
            .and_then(|v| v.as_str())
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty());
        let tag_description = json_field(dobj, "tagDescription", "tag_description")
            .and_then(|v| v.as_str())
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty());

        let recommended = json_field(dobj, "recommended", "recommended")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);
        let disabled = json_field(dobj, "disabled", "disabled")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);
        let beta = json_field(dobj, "beta", "beta")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);
        let beta_warning_message = json_field(dobj, "betaWarningMessage", "beta_warning_message")
            .and_then(|v| v.as_str())
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty());

        let supports_images = json_field(dobj, "supportsImages", "supports_images")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);
        let supports_thinking = json_field(dobj, "supportsThinking", "supports_thinking")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);
        let thinking_budget = json_field(dobj, "thinkingBudget", "thinking_budget")
            .and_then(|v| v.as_i64());
        let min_thinking_budget = json_field(dobj, "minThinkingBudget", "min_thinking_budget")
            .and_then(|v| v.as_i64());

        let max_tokens = json_field(dobj, "maxTokens", "max_tokens")
            .and_then(|v| v.as_u64())
            .filter(|&n| n > 0)
            .unwrap_or(1_048_576);
        let max_output_tokens = json_field(dobj, "maxOutputTokens", "max_output_tokens")
            .and_then(|v| v.as_u64())
            .filter(|&n| n > 0)
            .unwrap_or(65_536);

        let quota_obj = json_field(dobj, "quotaInfo", "quota_info").and_then(|v| v.as_object());
        let remaining_fraction = quota_obj
            .and_then(|q| json_field(q, "remainingFraction", "remaining_fraction"))
            .and_then(|v| v.as_f64());
        let reset_time = quota_obj
            .and_then(|q| json_field(q, "resetTime", "reset_time"))
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());

        let unavailable = disabled || remaining_fraction.map(|f| f <= 0.0).unwrap_or(false);
        let owned_by = infer_owned_by(&id, &display_name, dobj);

        let info = LiveModelInfo {
            id,
            display_name,
            owned_by,
            tag_title,
            tag_description,
            recommended,
            disabled,
            is_internal,
            beta,
            beta_warning_message,
            supports_images,
            supports_thinking,
            thinking_budget,
            min_thinking_budget,
            max_tokens,
            max_output_tokens,
            remaining_fraction,
            reset_time,
            unavailable,
        };
        if is_internal {
            internal_models.push(info);
        } else {
            models.push(info);
        }
    }

    let hydrogen_variants = [
        ("gemini-4-hydrogen-high", "Gemini 4 Hydrogen (XHigh)"),
        ("gemini-4-hydrogen-medium", "Gemini 4 Hydrogen (Medium)"),
        ("gemini-4-hydrogen-low", "Gemini 4 Hydrogen (Low)"),
    ];
    for (hid, hname) in &hydrogen_variants {
        if !models.iter().any(|m| m.id == *hid) {
            models.push(LiveModelInfo {
                id: hid.to_string(),
                display_name: hname.to_string(),
                owned_by: "google".to_string(),
                tag_title: Some("New".to_string()),
                tag_description: None,
                recommended: true,
                disabled: false,
                is_internal: false,
                beta: false,
                beta_warning_message: None,
                supports_images: true,
                supports_thinking: true,
                thinking_budget: Some(8192),
                min_thinking_budget: Some(32),
                max_tokens: 1_048_576,
                max_output_tokens: 65_536,
                remaining_fraction: Some(1.0),
                reset_time: None,
                unavailable: false,
            });
        }
    }

    if let Some(first_sort) = sorts.first_mut() {
        let top_models = vec![
            "gemini-4-hydrogen-medium".to_string(),
            "gemini-4-hydrogen-high".to_string(),
            "gemini-3.8-flash-high".to_string(),
            "claude-sonnet-4-6".to_string(),
            "claude-opus-4-6-thinking".to_string(),
            "gpt-oss-120b-medium".to_string(),
        ];
        for tm in top_models.into_iter().rev() {
            if !first_sort.model_ids.contains(&tm) {
                first_sort.model_ids.insert(0, tm);
            }
        }
    }

    if models.is_empty() && internal_models.is_empty() {
        return None;
    }

    let active_model = choose_best_active_model(
        current_default,
        &default_agent_model_id,
        &models,
        &deprecated_model_ids,
    );

    Some(LiveCatalogState {
        fetched_at_ms: now_ms(),
        source: "cloudcode_live".to_string(),
        project_id: if project_id.trim().is_empty() {
            "aicode-consumers".to_string()
        } else {
            project_id.trim().to_string()
        },
        default_agent_model_id,
        active_model,
        models,
        deprecated_model_ids,
        sorts,
        internal_models,
        grouped_models,
        raw_top_keys,
        load_code_assist_summary: Value::Null,
        last_error: None,
    })
}

fn choose_best_active_model(
    current_default: &str,
    default_agent_model_id: &str,
    models: &[LiveModelInfo],
    deprecated_model_ids: &HashMap<String, String>,
) -> String {
    let cur = current_default.trim();
    if !cur.is_empty() {
        if let Some(m) = models.iter().find(|m| m.id == cur && !m.disabled) {
            return m.id.clone();
        }
        if let Some(reroute) = deprecated_model_ids.get(cur) {
            if let Some(m) = models.iter().find(|m| m.id == *reroute && !m.disabled) {
                return m.id.clone();
            }
        }
        // Heuristic transition match (e.g. guessed "gemini-4-hydrogen-medium" -> real Hydrogen model)
        if let Some(matched) = heuristic_match_model(cur, models) {
            return matched;
        }
    }

    if !default_agent_model_id.is_empty() {
        if let Some(m) = models
            .iter()
            .find(|m| m.id == default_agent_model_id && !m.disabled)
        {
            return m.id.clone();
        }
    }

    models
        .iter()
        .find(|m| m.recommended && !m.unavailable)
        .or_else(|| models.iter().find(|m| !m.unavailable))
        .or_else(|| models.iter().find(|m| !m.disabled))
        .or_else(|| models.first())
        .map(|m| m.id.clone())
        .unwrap_or_default()
}

fn tokenize_model_hint(s: &str) -> Vec<String> {
    s.to_ascii_lowercase()
        .split(|c: char| !c.is_ascii_alphanumeric() && c != '.')
        .filter(|t| !t.is_empty())
        .map(|t| t.to_string())
        .collect()
}

fn heuristic_match_model(requested: &str, models: &[LiveModelInfo]) -> Option<String> {
    let req_lower = requested.trim().to_ascii_lowercase();
    if req_lower.is_empty() {
        return None;
    }

    // 1. Case-insensitive exact ID or displayName match
    for m in models {
        if !m.disabled
            && (m.id.eq_ignore_ascii_case(&req_lower)
                || m.display_name.eq_ignore_ascii_case(&req_lower))
        {
            return Some(m.id.clone());
        }
    }

    // 2. Token overlap score (ignores "local" models unless requested)
    let req_tokens = tokenize_model_hint(&req_lower);
    if req_tokens.is_empty() {
        return None;
    }
    let mut best: Option<(i32, String)> = None;
    for m in models {
        if m.disabled {
            continue;
        }
        let cand_text = format!("{} {}", m.id, m.display_name).to_ascii_lowercase();
        let cand_tokens: HashSet<String> = tokenize_model_hint(&cand_text).into_iter().collect();
        let mut score = 0i32;
        for tok in &req_tokens {
            if cand_tokens.contains(tok) {
                score += if matches!(tok.as_str(), "gemini" | "claude" | "gpt") {
                    1
                } else {
                    4
                };
            }
        }
        // Require at least one distinctive non-brand token match (e.g. "hydrogen", "3.8", "sonnet")
        if score >= 5 {
            if !m.unavailable {
                score += 1;
            }
            if best.as_ref().map(|(bs, _)| score > *bs).unwrap_or(true) {
                best = Some((score, m.id.clone()));
            }
        }
    }
    best.map(|(_, id)| id)
}

fn write_json_atomic(path: &Path, val: &Value) {
    if let Some(parent) = path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    let Ok(pretty) = serde_json::to_string_pretty(val) else {
        return;
    };
    let tmp = path.with_extension(format!("json.tmp.{}", std::process::id()));
    if fs::write(&tmp, pretty).is_ok() {
        let _ = fs::rename(&tmp, path);
    }
}

fn mirror_config_paths(config_dir: &Path, filename: &str) -> Vec<std::path::PathBuf> {
    let mut targets = vec![config_dir.join(filename)];
    let apps_cfg = Path::new("/opt/floworkos/apps/connector/config").join(filename);
    if apps_cfg.parent().map(|p| p.is_dir()).unwrap_or(false) && !targets.contains(&apps_cfg) {
        targets.push(apps_cfg);
    }
    targets
}

impl ModelsSyncManager {
    pub fn new(config: &ConfigManager) -> Self {
        let fallback = Self::build_fallback_from_config(config);
        Self {
            cache: RwLock::new(fallback),
            sync_lock: Mutex::new(()),
        }
    }

    pub fn build_fallback_from_config(config: &ConfigManager) -> LiveCatalogState {
        let cfg = config.get_models();
        let raw_val = config.read_json_cached("models.json", json!({}));
        let project_id = raw_val
            .get("project_id")
            .and_then(|v| v.as_str())
            .unwrap_or("aicode-consumers")
            .to_string();
        let default_agent_model_id = raw_val
            .get("default_agent_model_id")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let models: Vec<LiveModelInfo> = cfg
            .catalog
            .iter()
            .filter(|m| m.owned_by != "ollama")
            .map(|m| LiveModelInfo {
                id: m.id.clone(),
                display_name: m.name.clone(),
                owned_by: m.owned_by.clone(),
                tag_title: None,
                tag_description: None,
                recommended: m.id == cfg.default_model,
                disabled: false,
                is_internal: false,
                beta: false,
                beta_warning_message: None,
                supports_images: true,
                supports_thinking: true,
                thinking_budget: None,
                min_thinking_budget: None,
                max_tokens: 1_048_576,
                max_output_tokens: 65_536,
                remaining_fraction: None,
                reset_time: None,
                unavailable: false,
            })
            .collect();

        LiveCatalogState {
            fetched_at_ms: 0,
            source: "local_fallback".to_string(),
            project_id,
            default_agent_model_id,
            active_model: cfg.default_model,
            models,
            deprecated_model_ids: HashMap::new(),
            sorts: Vec::new(),
            internal_models: Vec::new(),
            grouped_models: Value::Null,
            raw_top_keys: Vec::new(),
            load_code_assist_summary: Value::Null,
            last_error: None,
        }
    }

    pub async fn get_cached(&self) -> LiveCatalogState {
        self.cache.read().await.clone()
    }

    pub async fn get_or_fetch(
        &self,
        vault_mgr: &VaultManager,
        http: &Client,
        force_refresh: bool,
    ) -> LiveCatalogState {
        if !force_refresh {
            let guard = self.cache.read().await;
            if guard.source == "cloudcode_live"
                && !guard.models.is_empty()
                && (now_ms() - guard.fetched_at_ms) < CATALOG_TTL_MS
            {
                return guard.clone();
            }
        }

        let _lock = self.sync_lock.lock().await;
        if !force_refresh {
            let guard = self.cache.read().await;
            if guard.source == "cloudcode_live"
                && !guard.models.is_empty()
                && (now_ms() - guard.fetched_at_ms) < CATALOG_TTL_MS
            {
                return guard.clone();
            }
        }

        match self.fetch_from_cloudcode(vault_mgr, http).await {
            Ok(live) => {
                self.persist_synced_catalog(vault_mgr, &live).await;
                let mut guard = self.cache.write().await;
                *guard = live.clone();
                live
            }
            Err(err) => {
                let mut fallback = Self::build_fallback_from_config(&vault_mgr.config);
                let existing = self.cache.read().await.clone();
                if existing.source == "cloudcode_live" && !existing.models.is_empty() {
                    fallback = existing;
                }
                fallback.last_error = Some(err);
                let mut guard = self.cache.write().await;
                *guard = fallback.clone();
                fallback
            }
        }
    }

    async fn fetch_from_cloudcode(
        &self,
        vault_mgr: &VaultManager,
        http: &Client,
    ) -> Result<LiveCatalogState, String> {
        let vault = vault_mgr.load_vault().await;
        if vault.accounts.is_empty() {
            return Err("No Google accounts in pool".to_string());
        }

        let net = vault_mgr.config.get_network();
        let host = net.upstream_host.trim_end_matches('/').to_string();
        let ua = effective_cloudcode_user_agent(&net.user_agent);
        let current_default = vault_mgr.config.get_models().default_model;

        let max_try = vault.accounts.len().clamp(1, 5);
        let mut tried = HashSet::new();
        let mut last_err = "Unable to fetch available models".to_string();

        for _ in 0..max_try {
            let mut v = vault_mgr.load_vault().await;
            let Some(idx) = VaultManager::select_next_available_index_excluding(&mut v, &tried) else {
                break;
            };
            let mut acc = v.accounts[idx].clone();
            tried.insert(acc.id.clone());

            if !vault_mgr.ensure_account_token_valid(&mut acc).await {
                v.accounts[idx] = acc;
                vault_mgr.save_vault(&v).await;
                last_err = "Account token invalid".to_string();
                continue;
            }
            v.accounts[idx] = acc.clone();
            vault_mgr.save_vault(&v).await;

            // Step 1: Resolve cloudaicompanionProject & entitlement via :loadCodeAssist
            let mut resolved_project = String::new();
            let mut resolved_tier: Option<Value> = None;
            let mut load_summary = json!({ "account": acc.email });
            let load_url = format!("{}/v1internal:loadCodeAssist", host);
            let load_body = json!({
                "metadata": {
                    "ideType": "ANTIGRAVITY",
                    "ideVersion": "2.35.0",
                    "platform": "LINUX_AMD64",
                    "pluginType": "GEMINI"
                }
            });
            if let Ok(resp) = http
                .post(&load_url)
                .header("Authorization", format!("Bearer {}", acc.access_token))
                .header("User-Agent", &ua)
                .header("Content-Type", "application/json")
                .json(&load_body)
                .timeout(Duration::from_secs(10))
                .send()
                .await
            {
                let lstatus = resp.status().as_u16();
                if resp.status().is_success() {
                    if let Ok(ljson) = resp.json::<Value>().await {
                        if let Some(p) = ljson
                            .get("cloudaicompanionProject")
                            .or_else(|| ljson.get("cloudaicompanion_project"))
                        {
                            if let Some(s) = p.as_str() {
                                resolved_project = s.trim().to_string();
                            } else if let Some(s) = p.get("id").and_then(|x| x.as_str()) {
                                resolved_project = s.trim().to_string();
                            }
                        }
                        if let Some(tier) = ljson.get("paidTier").or_else(|| ljson.get("currentTier")) {
                            resolved_tier = Some(tier.clone());
                        }
                        load_summary = json!({
                            "account": acc.email,
                            "status": lstatus,
                            "currentTier": ljson.get("currentTier"),
                            "paidTier": ljson.get("paidTier"),
                            "cloudaicompanionProject": ljson.get("cloudaicompanionProject"),
                            "keys": ljson.as_object().map(|o| o.keys().cloned().collect::<Vec<_>>())
                        });
                    }
                } else {
                    let err_b = resp.text().await.unwrap_or_default();
                    load_summary = json!({
                        "account": acc.email,
                        "status": lstatus,
                        "error": err_b.chars().take(200).collect::<String>()
                    });
                }
            }

            // Step 2: Fetch live catalog via :fetchAvailableModels
            let fetch_url = format!("{}/v1internal:fetchAvailableModels", host);
            let mut req_bodies = Vec::new();
            if !resolved_project.is_empty() {
                if let Some(ref tier) = resolved_tier {
                    req_bodies.push(json!({ "project": resolved_project, "entitlement": { "userTier": tier } }));
                }
                req_bodies.push(json!({ "project": resolved_project }));
            }
            req_bodies.push(json!({}));

            for body in req_bodies {
                let res = http
                    .post(&fetch_url)
                    .header("Authorization", format!("Bearer {}", acc.access_token))
                    .header("User-Agent", &ua)
                    .header("Content-Type", "application/json")
                    .json(&body)
                    .timeout(Duration::from_secs(12))
                    .send()
                    .await;

                match res {
                    Ok(r) => {
                        let status = r.status();
                        if status.as_u16() == 401 {
                            let mut ref_acc = acc.clone();
                            let _ = vault_mgr.refresh_account_token(&mut ref_acc, true).await;
                            let mut v2 = vault_mgr.load_vault().await;
                            if let Some(pos) = v2.accounts.iter().position(|a| a.id == ref_acc.id) {
                                v2.accounts[pos] = ref_acc.clone();
                                vault_mgr.save_vault(&v2).await;
                            }
                            last_err = "401 Unauthorized".to_string();
                            break;
                        }
                        if !status.is_success() {
                            let txt = r.text().await.unwrap_or_default();
                            last_err = format!("HTTP {}: {}", status.as_u16(), txt.chars().take(180).collect::<String>());
                            continue;
                        }
                        match r.json::<Value>().await {
                            Ok(parsed) => {
                                let proj = if resolved_project.is_empty() {
                                    "aicode-consumers".to_string()
                                } else {
                                    resolved_project.clone()
                                };
                                if let Some(mut state) =
                                    parse_fetch_available_models_response(&parsed, &proj, &current_default)
                                {
                                    state.load_code_assist_summary = load_summary;
                                    println!(
                                        "[ModelsSync] ✅ Synced {} live CloudCode models (+{} internal, active: {}, project: {})",
                                        state.models.len(),
                                        state.internal_models.len(),
                                        state.active_model,
                                        state.project_id
                                    );
                                    return Ok(state);
                                }
                                last_err = "Empty models map from CloudCode".to_string();
                            }
                            Err(e) => {
                                last_err = format!("Failed parsing fetchAvailableModels JSON: {}", e);
                            }
                        }
                    }
                    Err(e) => {
                        last_err = e.to_string();
                    }
                }
            }
        }

        Err(last_err)
    }

    async fn persist_synced_catalog(&self, vault_mgr: &VaultManager, live: &LiveCatalogState) {
        let old_models_val = vault_mgr.config.read_json_cached("models.json", json!({}));
        let mut preserved_local = Vec::new();
        if let Some(arr) = old_models_val.get("catalog").and_then(|v| v.as_array()) {
            for item in arr {
                let owned = item.get("owned_by").and_then(|v| v.as_str()).unwrap_or("");
                if owned == "ollama" {
                    preserved_local.push(item.clone());
                }
            }
        }

        let mut catalog: Vec<Value> = live
            .models
            .iter()
            .map(|m| {
                json!({
                    "id": m.id,
                    "name": m.display_name,
                    "owned_by": m.owned_by,
                    "tag_title": m.tag_title,
                    "recommended": m.recommended,
                    "disabled": m.disabled,
                    "unavailable": m.unavailable,
                    "supports_thinking": m.supports_thinking,
                    "context_window": m.max_tokens,
                    "max_output_tokens": m.max_output_tokens
                })
            })
            .collect();
        catalog.extend(preserved_local);

        let available_models: Vec<Value> = live
            .models
            .iter()
            .map(|m| {
                json!({
                    "id": m.id,
                    "display_name": m.display_name,
                    "context_window": m.max_tokens,
                    "max_output_tokens": m.max_output_tokens,
                    "supports_thinking": m.supports_thinking,
                    "disabled": m.disabled
                })
            })
            .collect();

        let models_json = json!({
            "default_model": live.active_model,
            "default_agent_model_id": live.default_agent_model_id,
            "project_id": live.project_id,
            "source": live.source,
            "last_synced_at": Utc::now().to_rfc3339(),
            "deprecated_model_ids": live.deprecated_model_ids,
            "catalog": catalog,
            "available_models": available_models
        });

        for p in mirror_config_paths(&vault_mgr.config.paths.config_dir, "models.json") {
            write_json_atomic(&p, &models_json);
        }

        // Auto-heal settings.json and providers.json if they still point to an invalid/removed Google model
        let old_default = old_models_val
            .get("default_model")
            .and_then(|v| v.as_str())
            .unwrap_or("");
        if old_default != live.active_model && !live.active_model.is_empty() {
            self.sync_active_model_to_configs(vault_mgr, &live.active_model).await;
        }
    }

    async fn sync_active_model_to_configs(&self, vault_mgr: &VaultManager, model_id: &str) {
        let mut settings_val = vault_mgr.config.read_json_cached("settings.json", json!({}));
        if let Some(sobj) = settings_val.as_object_mut() {
            sobj.insert("single_model_lock".to_string(), json!(model_id));
            for p in mirror_config_paths(&vault_mgr.config.paths.config_dir, "settings.json") {
                write_json_atomic(&p, &Value::Object(sobj.clone()));
            }
        }

        let mut prov_val = vault_mgr.config.read_json_cached("providers.json", json!({}));
        if let Some(pobj) = prov_val.as_object_mut() {
            let has_inner = pobj
                .get("providers")
                .and_then(|v| v.as_object())
                .is_some();
            if has_inner {
                if let Some(inner) = pobj.get_mut("providers").and_then(|v| v.as_object_mut()) {
                    if let Some(gc) = inner.get_mut("google_cloudcode").and_then(|v| v.as_object_mut()) {
                        gc.insert("model".to_string(), json!(model_id));
                    }
                }
            } else if let Some(gc) = pobj.get_mut("google_cloudcode").and_then(|v| v.as_object_mut()) {
                gc.insert("model".to_string(), json!(model_id));
            }
            for p in mirror_config_paths(&vault_mgr.config.paths.config_dir, "providers.json") {
                write_json_atomic(&p, &Value::Object(pobj.clone()));
            }
        }
    }

    pub async fn select_active_model(
        &self,
        vault_mgr: &VaultManager,
        http: &Client,
        requested_model: &str,
    ) -> Result<String, String> {
        let target = requested_model.trim();
        if target.is_empty() {
            return Err("Model ID cannot be empty".to_string());
        }

        let mut live = self.get_or_fetch(vault_mgr, http, false).await;
        let resolved = if live.models.iter().any(|m| m.id == target) {
            target.to_string()
        } else if let Some(reroute) = live.deprecated_model_ids.get(target) {
            reroute.clone()
        } else if let Some(matched) = heuristic_match_model(target, &live.models) {
            matched
        } else {
            target.to_string()
        };

        live.active_model = resolved.clone();
        self.persist_synced_catalog(vault_mgr, &live).await;
        self.sync_active_model_to_configs(vault_mgr, &resolved).await;

        let mut guard = self.cache.write().await;
        *guard = live;
        Ok(resolved)
    }

    pub async fn resolve_for_upstream(
        &self,
        vault_mgr: &VaultManager,
        http: &Client,
        requested_model: &str,
    ) -> (String, String) {
        let live = self.get_or_fetch(vault_mgr, http, false).await;
        let project = if live.project_id.trim().is_empty() {
            "aicode-consumers".to_string()
        } else {
            live.project_id.clone()
        };

        let req = requested_model.trim();
        if req.is_empty() {
            let fallback = if !live.active_model.is_empty() {
                live.active_model
            } else {
                vault_mgr.config.get_models().default_model
            };
            return (fallback, project);
        }

        // Special routing for Hydrogen models:
        // Antigravity UI and Connector expose gemini-4-hydrogen-medium, high, low.
        // Google CloudCode live backend endpoint expects gemini-4-hydrogen-sonar.
        if req.starts_with("gemini-4-hydrogen") {
            if live.models.iter().any(|m| m.id == "gemini-4-hydrogen-sonar") {
                return ("gemini-4-hydrogen-sonar".to_string(), project);
            }
        }

        if live.models.iter().any(|m| m.id == req) {
            return (req.to_string(), project);
        }

        if let Some(reroute) = live.deprecated_model_ids.get(req) {
            if live.models.iter().any(|m| m.id == *reroute) {
                return (reroute.clone(), project);
            }
        }

        if live.source == "cloudcode_live" && !live.models.is_empty() {
            if let Some(matched) = heuristic_match_model(req, &live.models) {
                return (matched, project);
            }
            if !live.active_model.is_empty() {
                return (live.active_model, project);
            }
        }

        (req.to_string(), project)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_live_models_hides_internal_and_reroutes_deprecated() {
        let payload = json!({
            "defaultAgentModelId": "gemini-4-hydrogen",
            "agentModelSorts": [{
                "displayName": "Recommended",
                "groups": [{
                    "displayName": "Gemini",
                    "modelIds": ["gemini-4-hydrogen", "claude-sonnet-4-6"]
                }]
            }],
            "deprecatedModelIds": {
                "gemini-3.8-flash-high": { "newModelId": "gemini-4-hydrogen" }
            },
            "models": {
                "gemini-4-hydrogen": {
                    "displayName": "Gemini 4 Hydrogen",
                    "tagTitle": "New",
                    "recommended": true,
                    "supportsImages": true,
                    "supportsThinking": true,
                    "maxTokens": 1048576,
                    "maxOutputTokens": 65536,
                    "quotaInfo": { "remainingFraction": 1.0 }
                },
                "claude-sonnet-4-6": {
                    "displayName": "Claude Sonnet 4.6 (Thinking)",
                    "modelProvider": "MODEL_PROVIDER_ANTHROPIC",
                    "tagTitle": "Notice",
                    "quotaInfo": { "remainingFraction": 0.8 }
                },
                "internal-debug-model": {
                    "displayName": "Internal Debug",
                    "isInternal": true
                },
                "gemini-4-carbon": {
                    "displayName": "Gemini 4 Carbon",
                    "disabled": true,
                    "quotaInfo": { "remainingFraction": 0.0 }
                }
            }
        });

        let state = parse_fetch_available_models_response(
            &payload,
            "my-project-123",
            "gemini-3.8-flash-high",
        )
        .unwrap();

        assert_eq!(state.project_id, "my-project-123");
        // Internal model excluded
        assert!(!state.models.iter().any(|m| m.id == "internal-debug-model"));
        // Ordered per agentModelSorts first
        assert_eq!(state.models[0].id, "gemini-4-hydrogen");
        assert_eq!(state.models[0].tag_title.as_deref(), Some("New"));
        assert_eq!(state.models[1].id, "claude-sonnet-4-6");
        assert_eq!(state.models[1].owned_by, "anthropic");
        assert!(state.models.iter().find(|m| m.id == "gemini-4-carbon").unwrap().unavailable);
        // Deprecated 3.8 automatically rerouted to gemini-4-hydrogen
        assert_eq!(state.active_model, "gemini-4-hydrogen");
    }

    #[test]
    fn auto_heals_guessed_model_name_when_removed_or_invalid() {
        let payload = json!({
            "defaultAgentModelId": "gemini-4-hydrogen-real",
            "models": {
                "gemini-4-hydrogen-real": {
                    "displayName": "Gemini 4 Hydrogen Medium",
                    "recommended": true
                }
            }
        });

        let state = parse_fetch_available_models_response(
            &payload,
            "aicode-consumers",
            "gemini-4-hydrogen-medium",
        )
        .unwrap();
        assert_eq!(state.active_model, "gemini-4-hydrogen-real");
    }
}
