use crate::mock_engine::MockEngine;
use shared_types::models::{AuthTokens, PluginItem, SkillDetail, SkillItem, SkillVersionItem};
use std::sync::Arc;

#[derive(Clone)]
pub struct AxClient {
    pub api_base: String,
    pub mock_mode: bool,
    mock: Arc<MockEngine>,
}

impl AxClient {
    pub fn new(api_base: String, mock_mode: bool) -> Self {
        Self {
            api_base,
            mock_mode,
            mock: Arc::new(MockEngine::new()),
        }
    }

    pub fn request_otp(&self, email: &str) -> Result<(), String> {
        if self.mock_mode {
            return self.mock.request_otp(email);
        }
        // When real network call is wired, falls back to mock if server unreachable
        self.mock.request_otp(email)
    }

    pub fn verify_otp(&self, email: &str, otp: &str) -> Result<(), String> {
        if self.mock_mode {
            return self.mock.verify_otp(email, otp);
        }
        self.mock.verify_otp(email, otp)
    }

    pub fn login(&self, email: &str, password: &str) -> Result<AuthTokens, String> {
        if self.mock_mode {
            return self.mock.login(email, password);
        }
        self.mock.login(email, password)
    }

    pub fn fetch_skills(&self, query: Option<&str>, page: usize, page_size: usize) -> Vec<SkillItem> {
        if self.mock_mode {
            return self.mock.fetch_skills(query, page, page_size);
        }
        self.mock.fetch_skills(query, page, page_size)
    }

    pub fn get_skill_detail(&self, id: u64) -> Result<SkillDetail, String> {
        if self.mock_mode {
            return self.mock.get_skill_detail(id);
        }
        self.mock.get_skill_detail(id)
    }

    pub fn get_skill_versions(&self, id: u64) -> Vec<SkillVersionItem> {
        if self.mock_mode {
            return self.mock.get_skill_versions(id);
        }
        self.mock.get_skill_versions(id)
    }

    pub fn download_skill_zip(&self, id: u64, skill_name: &str) -> Result<Vec<u8>, String> {
        if self.mock_mode {
            return self.mock.generate_skill_zip(id, skill_name);
        }
        self.mock.generate_skill_zip(id, skill_name)
    }

    pub fn fetch_mcp_catalog(&self) -> Vec<PluginItem> {
        if self.mock_mode {
            return self.mock.fetch_mcp_catalog();
        }
        self.mock.fetch_mcp_catalog()
    }
}
