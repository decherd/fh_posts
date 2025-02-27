"""Core functionality for the fh-posts package."""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['logger', 'Post', 'extract_frontmatter', 'extract_notebook_frontmatter', 'get_post_date', 'load_posts', 'parse_tag',
           'execute_code', 'process_code_block', 'render_markdown_post', 'render_notebook_post']

# %% ../nbs/00_core.ipynb 3
from pathlib import Path
import yaml
from fastcore.basics import AttrDict
from fasthtml.common import to_xml, NotStr
from monsterui.all import *
import nbformat
import re
from bs4 import BeautifulSoup
import io
import sys
from typing import List, Dict, Optional
import logging
from datetime import datetime
from fastcore.test import *

# %% ../nbs/00_core.ipynb 4
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fh-posts")

# %% ../nbs/00_core.ipynb 6
class Post:
    """Represents a blog post with its metadata and content. This class provides methods 
    to render the post content with optional code execution and formatting options."""
    def __init__(
            self, # The post to initialize
            path: Path, # The path to the post
            metadata: AttrDict, # The metadata for the post
            slug: str # The slug for the post
            ):
        self.path = path
        self.metadata = metadata
        self.slug = slug
        self._execution_state = {}
        
    def __getitem__(self, key):
        return self.metadata[key]
    
    def __getattr__(self, name):
        if name in self.metadata:
            return self.metadata[name]
        raise AttributeError(f"'Post' object has no attribute '{name}'")
    
    def render(
            self, # The post to render
            open_links_new_window: bool = False, # Whether to open links in a new window
            live_label: bool = True # Whether to show the live label
            ) -> NotStr:
        """Render the post content with code execution as specified by tags."""
        if self.path.suffix == '.md':
            return render_markdown_post(self, open_links_new_window, live_label)
        elif self.path.suffix == '.ipynb':
            return render_notebook_post(self, open_links_new_window, live_label)
        else:
            raise ValueError(f"Unsupported file type: {self.path.suffix}")
    
    def __repr__(self):
        return f"Post(slug='{self.slug}', title='{self.metadata.get('title', 'Untitled')}', path='{self.path}')"

# %% ../nbs/00_core.ipynb 10
def extract_frontmatter(
        file_path: Path # The path to the file to extract the frontmatter from
        ) -> AttrDict:
    """Extract YAML frontmatter from a Markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the file starts with frontmatter (---)
    if content.startswith('---'):
        # Split on the second --- to get frontmatter
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                yaml_content = parts[1].strip()
                metadata = yaml.safe_load(yaml_content) or {}
                return AttrDict(metadata)
            except yaml.YAMLError as e:
                logger.error(f"Error parsing YAML frontmatter in {file_path}: {e}")
    
    # Return empty metadata if no frontmatter found
    return AttrDict({})

# %% ../nbs/00_core.ipynb 14
def extract_notebook_frontmatter(
        file_path: Path # The path to the notebook to extract the frontmatter from
        ) -> AttrDict:
    """Extract YAML frontmatter from a Jupyter Notebook file."""
    notebook = nbformat.read(file_path, as_version=4)
    
    # Check if the first cell is raw and contains frontmatter
    if len(notebook.cells) > 0 and notebook.cells[0].cell_type == 'raw':
        cell_content = notebook.cells[0].source
        if cell_content.startswith('---') and '---' in cell_content[3:]:
            try:
                # Extract content between first two --- markers
                yaml_content = cell_content.split('---', 2)[1].strip()
                metadata = yaml.safe_load(yaml_content) or {}
                return AttrDict(metadata)
            except yaml.YAMLError as e:
                logger.error(f"Error parsing YAML frontmatter in {file_path}: {e}")
    
    # Return empty metadata if no frontmatter found
    return AttrDict({})

# %% ../nbs/00_core.ipynb 19
def get_post_date(
        post, # The post to get the date from
        date_format="%B %d, %Y" # The format string for the date i.e. "January 01, 2025"
        ) -> datetime:
    """Extract date from post for sorting."""
    
    if 'date' in post.metadata:
        try:
            return datetime.strptime(post.metadata['date'], date_format)
        except:
            pass
    return datetime.min

# %% ../nbs/00_core.ipynb 21
def load_posts(
        path: str|Path, # The path to the directory containing the posts
        date_format: str = "%B %d, %Y" # The format string for the date i.e. "January 01, 2025"
        ) -> List[Post]:
    """Load all posts from the specified directory. Extracts frontmatter from markdown files and notebooks
    with `extract_frontmatter` and `extract_notebook_frontmatter` respectively. Specify optional date format 
    string for `get_post_date` to sort posts by date."""
    
    posts_dir = Path(path)
    posts = []
    
    # Process Markdown files
    for file_path in posts_dir.glob("*.md"):
        try:
            metadata = extract_frontmatter(file_path)
            slug = file_path.stem
            posts.append(Post(file_path, metadata, slug))
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
    
    # Process Jupyter Notebook files
    for file_path in posts_dir.glob("*.ipynb"):
        try:
            metadata = extract_notebook_frontmatter(file_path)
            slug = file_path.stem
            posts.append(Post(file_path, metadata, slug))
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
    
    # Sort posts by date if available, newest first
    return sorted(posts, key=lambda post: get_post_date(post), reverse=True)

# %% ../nbs/00_core.ipynb 27
def parse_tag(tag_str: str) -> Dict[str, bool]:
    """Parse a tag string into a dict of tag properties e.g., 'python:run:hide-in'."""
    # Default properties
    tag_props = {
        'run': False,       # Execute the code
        'hide_in': False,   # Hide the input code
        'hide_out': False,  # Hide the output
        'hide_call': False,      # Hide the final call line
    }
    
    if not tag_str:
        return tag_props
    
    # Split the tag string and process each part
    parts = tag_str.split(':')
    
    # First part should be 'python'
    if len(parts) == 0 or parts[0] != 'python':
        return tag_props
    
    
    # Process the rest of the parts
    for part in parts[1:]:
        if part == 'run':
            tag_props['run'] = True
        elif part == 'hide':
            tag_props['hide_in'] = True
            tag_props['hide_out'] = True
        elif part == 'hide-in':
            tag_props['hide_in'] = True
        elif part == 'hide-out':
            tag_props['hide_out'] = True
        elif part == 'hide-call':
            tag_props['hide_call'] = True
    
    return tag_props

# %% ../nbs/00_core.ipynb 31
def execute_code(
        code: str, # The code to execute
        namespace: Optional[Dict] = None # Optional namespace to use for execution
        ) -> Dict: # Returns a dict with keys: output (captured stdout), error (captured stderr), result (last expression result), namespace (updated namespace)
    """Execute Python code and return the execution result."""
    if namespace is None:
        namespace = {}
    
    # Add default imports
    if 'from fasthtml.common import' not in code and 'fasthtml' not in namespace:
        exec('from fasthtml.common import *', namespace)
    if 'from monsterui.all import' not in code and 'monsterui' not in namespace:
        exec('from monsterui.all import *', namespace)
    
    # Capture stdout and stderr
    orig_stdout, orig_stderr = sys.stdout, sys.stderr
    captured_output = io.StringIO()
    sys.stdout = sys.stderr = captured_output
    
    result = None
    error = None
    
    try:
        # Execute the code
        exec_result = exec(code, namespace)
        
        # Try to get the last expression result if it's an expression
        try:
            last_line = code.strip().split('\n')[-1]
            if not (last_line.startswith('#') or 
                    re.match(r'^\s*$', last_line) or
                    '=' in last_line or 
                    last_line.startswith('def ') or
                    last_line.startswith('class ') or
                    last_line.startswith('import ') or
                    last_line.startswith('from ') or
                    last_line.startswith('print(')):  # Skip print statements
                # It seems to be an expression, re-evaluate to get its result
                result = eval(last_line, namespace)
        except:
            # Not an expression or other issue, use exec result
            result = exec_result
    except Exception as e:
        error = str(e)
    finally:
        # Restore stdout and stderr
        output = captured_output.getvalue()
        sys.stdout, sys.stderr = orig_stdout, orig_stderr
    
    return {
        'output': output,
        'error': error,
        'result': result,
        'namespace': namespace
    }

# %% ../nbs/00_core.ipynb 35
def process_code_block(
        tag_props: Dict[str, bool], # Dict of tag properties    
        code: str, # Python code to execute
        namespace: Optional[Dict] = None # Optional namespace to use for execution
        ) -> Dict: # Returns a dict with keys: show_code, show_output, code_html, output_html, namespace
    """Process a code block based on its tag properties."""
    
    result = {
        'show_code': not tag_props['hide_in'],
        'show_output': not tag_props['hide_out'],
        'code_html': '',
        'output_html': '',
        'namespace': namespace or {}
    }
    
    # Process code for display (handle the hide-call option)
    display_code = code
    
    # Execute code if needed
    if tag_props['run']:
        execution_result = execute_code(code, result['namespace'])
        result['namespace'] = execution_result['namespace']
        
        # Format output HTML
        output_html = []
        
        # Add stdout output if there's any
        if execution_result['output']:
            output_html.append(f'<pre class="output">{execution_result["output"]}</pre>')
        
        # Add error message if there's any
        if execution_result['error']:
            output_html.append(f'<pre class="error">{execution_result["error"]}</pre>')
        
        # Add result if there's any and it's not None
        if execution_result['result'] is not None:
            try:
                # Convert result to FastHTML XML
                result_html = to_xml(execution_result['result'])
                output_html.append(str(result_html))
            except:
                # Fallback to string representation
                output_html.append(f'<pre class="result">{execution_result["result"]}</pre>')
        
        result['output_html'] = ''.join(output_html)
    
    # Process code for display (handle hide-call option if needed)
    if tag_props['hide_call']:
        # If not showing the call, try to hide the last line if it's an expression
        lines = display_code.split('\n')
        last_non_empty = next((i for i in range(len(lines)-1, -1, -1) 
                              if lines[i].strip() and not lines[i].strip().startswith('#')), -1)
        
        if last_non_empty >= 0 and not ('=' in lines[last_non_empty] 
                                       or lines[last_non_empty].strip().startswith(('def ', 'class ', 'import ', 'from '))):
            lines = lines[:last_non_empty] + lines[last_non_empty+1:]
            display_code = '\n'.join(lines)
    
    # Format code HTML
    if result['show_code']:
        result['code_html'] = f'<pre><code class="language-python">{display_code}</code></pre>'
    
    return result

# %% ../nbs/00_core.ipynb 37
def render_markdown_post(
        post: Post, # The post to render
        open_links_new_window: bool = False, 
        live_label: bool = True
        ) -> NotStr: # The rendered HTML in a NotStr object (FastHTML object)
    """Render a Markdown post with code execution."""
    
    with open(post.path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove frontmatter if present
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    
    # Split the content on code blocks
    parts = re.split(r'```(.*?)```', content, flags=re.DOTALL)
    
    # Initialize variables
    processed_parts = []
    namespace = {}  # Shared execution namespace for all code blocks
    
    # Process each part
    for i, part in enumerate(parts):
        if i % 2 == 0:  # Not a code block
            # Convert markdown to HTML
            html = str(render_md(part))
            processed_parts.append(html)
        else:  # Code block
            # Extract tag and code
            lines = part.split('\n', 1)
            tag_str = lines[0].strip() if lines else ''
            code = lines[1] if len(lines) > 1 else ''
            
            # Skip non-Python code blocks
            if not tag_str.startswith('python'):
                processed_parts.append(f'```{part}```')
                continue
            
            # Parse the tag
            tag_props = parse_tag(tag_str)
            
            # Process the code block
            result = process_code_block(tag_props, code, namespace)
            namespace = result['namespace']  # Update the namespace
            
            # Add the processed code and output to the result
            if result['show_code']:
                processed_parts.append(result['code_html'])
            
            if tag_props['run'] and result['show_output'] and result['output_html']:
                processed_parts.append('<div class="mb-4"></div>')
                processed_parts.append(result['output_html'])
                if live_label:
                    processed_parts.append('<div class="text-gray-400 text-sm mt-2 italic">↑ Live rendered output</div>')
            processed_parts.append('<div class="mb-8"></div>')
    
    # Combine all parts
    html_content = ''.join(processed_parts)
    
    # Process links if needed
    if open_links_new_window:
        soup = BeautifulSoup(html_content, 'html.parser')
        for link in soup.find_all('a'):
            if not link.get('href', '').startswith('/'):
                link['target'] = '_blank'
                link['rel'] = 'noopener noreferrer'
        html_content = str(soup)
    
    return NotStr(html_content)

# %% ../nbs/00_core.ipynb 39
def render_notebook_post(
        post: Post, # The post to render
        open_links_new_window: bool = False, 
        live_label: bool = True) -> NotStr:
    """Render a Jupyter Notebook post with code execution."""
    # Load the notebook
    notebook = nbformat.read(post.path, as_version=4)
    
    # Initialize variables
    processed_parts = []
    namespace = {}  # Shared execution namespace
    
    # Skip the frontmatter cell if present
    start_index = 1 if (len(notebook.cells) > 0 and notebook.cells[0].cell_type == 'raw') else 0
    
    # Process each cell
    for cell in notebook.cells[start_index:]:
        if cell.cell_type == 'markdown':
            # Convert markdown to HTML
            html = str(render_md(cell.source))
            processed_parts.append(html)
        
        elif cell.cell_type == 'code':
            # Extract tag from the first line if present
            lines = cell.source.split('\n')
            tag_str = ''
            
            # Check if the first line is a tag
            if lines and re.match(r'^\s*#\|python', lines[0]):
                # If the tag is just #|python with no options, treat it like the default
                if lines[0].strip() == '#|python':
                    tag_str = 'python:run:hide-out'
                else:
                    tag_str = lines[0].strip()[2:]  # Remove the #| prefix
                code = '\n'.join(lines[1:])  # Rest of the code
            else:
                code = cell.source  # Use the entire cell source 
                # Default tag for notebook cells (Only set this for cells without explicit tags)
                tag_str = 'python:run:hide'
            
            # Parse the tag
            tag_props = parse_tag(tag_str)
            
            # Process the code cell
            result = process_code_block(tag_props, code, namespace)
            namespace = result['namespace']  # Update the namespace
            
            # Add the processed code and output to the result
            if result['show_code']:
                processed_parts.append(result['code_html'])
            
            if tag_props['run'] and result['show_output'] and result['output_html']:
                processed_parts.append('<div class="mb-4"></div>')
                processed_parts.append(result['output_html'])
                if live_label:
                    processed_parts.append('<div class="text-gray-400 text-sm mt-2 italic">↑ Live rendered output</div>')
            processed_parts.append('<div class="mb-8"></div>')
    
    # Combine all parts
    html_content = ''.join(processed_parts)
    
    # Process links if needed
    if open_links_new_window:
        soup = BeautifulSoup(html_content, 'html.parser')
        for link in soup.find_all('a'):
            if not link.get('href', '').startswith('/'):
                link['target'] = '_blank'
                link['rel'] = 'noopener noreferrer'
        html_content = str(soup)
    
    return NotStr(html_content)
