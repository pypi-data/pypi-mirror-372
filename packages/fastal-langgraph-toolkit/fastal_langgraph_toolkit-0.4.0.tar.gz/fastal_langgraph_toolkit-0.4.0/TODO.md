# Fastal LangGraph Toolkit - Development TODO

## Version 1.0.0 Migration Plan

### Breaking Changes Planned for v1.0.0

#### 1. Factory Classes Privatization
The following factory classes will be made private (internal implementation details) in v1.0.0:

- `LLMFactory` → `_LLMFactory`
- `EmbeddingFactory` → `_EmbeddingFactory`  
- `STTFactory` → `_STTFactory`

**Current Status (v0.4.0):**
- Deprecation warnings added to all three factory classes
- Users are warned to migrate to `ModelFactory` API
- Full backward compatibility maintained

**Migration Timeline:**
- **v0.4.0** (Current): Deprecation warnings added
- **v0.5.0 - v0.9.x**: Continue deprecation warnings, update documentation
- **v1.0.0**: Make classes private, remove from public API

**User Migration Path:**
```python
# OLD (deprecated in v0.4.0, will break in v1.0.0)
from fastal.langgraph.toolkit.models import LLMFactory, EmbeddingFactory, STTFactory

llm = LLMFactory.create_llm("openai", "gpt-4", config)
embeddings = EmbeddingFactory.create_embeddings("openai", "text-embedding-3-small", config)
stt = STTFactory.create_stt("openai", "whisper-1", config)

# NEW (recommended from v0.4.0+)
from fastal.langgraph.toolkit import ModelFactory

llm = ModelFactory.create_llm("openai", "gpt-4", config)
embeddings = ModelFactory.create_embeddings("openai", "text-embedding-3-small", config)
stt = ModelFactory.create_stt("openai", "whisper-1", config)
```

#### 2. Module Structure Changes

**Files to Modify in v1.0.0:**

1. `/src/fastal/langgraph/toolkit/models/factory.py`:
   - Rename `LLMFactory` → `_LLMFactory`
   - Rename `EmbeddingFactory` → `_EmbeddingFactory`
   - Rename `STTFactory` → `_STTFactory`
   - Remove deprecation warnings

2. `/src/fastal/langgraph/toolkit/models/__init__.py`:
   - Update imports to use private names internally
   - Remove factory classes from `__all__` export
   - Keep `ModelFactory` as the only public factory

3. Update all internal references:
   - ModelFactory should import `_LLMFactory`, `_EmbeddingFactory`, `_STTFactory`
   - No other modules should import these directly

#### 3. Test Updates Required

**Test files to update in v1.0.0:**
- `/tests/test_stt.py`: Update to use `ModelFactory` instead of direct `STTFactory`
- Any other tests using factory classes directly

### Non-Breaking Improvements for Future Versions

#### v0.5.0 - Extended STT Providers
- [ ] Add Google Cloud Speech-to-Text provider
- [ ] Add Azure Cognitive Services STT provider
- [ ] Add speaker diarization support
- [ ] Add batch processing for STT

#### v0.6.0 - Text-to-Speech Support
- [ ] Add TTS factory and base classes
- [ ] Implement OpenAI TTS provider
- [ ] Implement Google Cloud TTS provider
- [ ] Implement ElevenLabs provider
- [ ] Implement Azure TTS provider

#### v0.7.0 - v0.9.0 - Feature Enhancements
- [ ] Add streaming support for STT
- [ ] Add real-time transcription capabilities
- [ ] Add advanced error recovery mechanisms
- [ ] Performance optimizations
- [ ] Additional provider implementations

### Documentation Updates

Before v1.0.0 release:
1. Update README.md to emphasize `ModelFactory` as primary API
2. Add migration guide for users upgrading from v0.x to v1.0
3. Update all example code to use `ModelFactory`
4. Create comprehensive changelog

### Semantic Versioning Strategy

- **v0.x.y**: Non-breaking additions, deprecations allowed
- **v0.x.0**: New features, backward compatible
- **v0.x.y**: Bug fixes and patches
- **v1.0.0**: First stable release with breaking changes
- Post-v1.0.0: Follow strict semver (breaking changes = major version bump)

### Release Checklist for v1.0.0

- [ ] All deprecation warnings have been in place for at least 3 minor versions
- [ ] Migration guide published and communicated
- [ ] All tests updated to new API
- [ ] Documentation fully updated
- [ ] Changelog with clear breaking changes section
- [ ] Consider providing a compatibility shim package for gradual migration

## Notes

- This TODO file tracks long-term architectural changes
- Regular feature additions and bug fixes are tracked in GitHub Issues
- Breaking changes should be rare and well-communicated
- User experience and backward compatibility are priorities

---

*Last Updated: 2025-08-26*  
*Next Review: Before v0.5.0 release*