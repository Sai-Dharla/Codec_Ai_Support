"""
Compatibility helper to ensure pure-python regex fallback is loaded
before packages like transformers or nltk attempt to import C-compiled regex DLLs.
"""
import sys
import re

if 'regex' not in sys.modules or not hasattr(sys.modules['regex'], 'compile'):
    try:
        import regex
    except (ImportError, OSError):
        class _SafeRegexModule:
            Pattern = re.Pattern
            Regex = re.Pattern
            error = re.error
            ASCII = re.ASCII
            IGNORECASE = re.IGNORECASE
            LOCALE = re.LOCALE
            UNICODE = re.UNICODE
            MULTILINE = re.MULTILINE
            DOTALL = re.DOTALL
            VERBOSE = re.VERBOSE
            
            def compile(self, pattern, *args, **kwargs):
                if isinstance(pattern, str):
                    cleaned_pat = (
                        pattern.replace(r'[^\p{L}\p{N}]', r'[^\w]')
                               .replace(r'[\p{L}\p{N}]', r'[\w]')
                               .replace(r'\p{L}', r'[a-zA-Z]')
                               .replace(r'\p{N}', r'[0-9]')
                    )
                else:
                    cleaned_pat = pattern
                return re.compile(cleaned_pat, *args, **kwargs)

            def sub(self, pattern, repl, string, *args, **kwargs):
                return self.compile(pattern).sub(repl, string, *args, **kwargs)

            def match(self, pattern, string, *args, **kwargs):
                return self.compile(pattern).match(string, *args, **kwargs)

            def search(self, pattern, string, *args, **kwargs):
                return self.compile(pattern).search(string, *args, **kwargs)

            def findall(self, pattern, string, *args, **kwargs):
                return self.compile(pattern).findall(string, *args, **kwargs)

            def split(self, pattern, string, *args, **kwargs):
                return self.compile(pattern).split(string, *args, **kwargs)

            def __getattr__(self, name):
                return getattr(re, name)

        sys.modules['regex'] = _SafeRegexModule()

