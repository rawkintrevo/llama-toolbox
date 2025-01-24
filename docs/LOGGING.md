# Logging Configuration

The llama-toolbox uses Python's standard logging module. To configure logging:

```python  
import logging  
logging.getLogger('llama_toolbox').setLevel(logging.DEBUG)  
```

OR

```bash
export LLAMA_TOOLBOX_LOG_LEVEL=DEBUG  
```

Available levels: DEBUG, INFO, WARNING (default), ERROR, CRITICAL


**Key Benefits:**
- Standardized format: `2023-12-20 15:30:45 - llama_toolbox.github.commit_file - INFO - Message`
- Hierarchical logging using module paths
- Environment variable control (LLAMA_TOOLBOX_LOG_LEVEL)
- Both library and standalone usage support
- Contextual logging with tool/operation names  