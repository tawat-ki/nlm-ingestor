# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.3.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
#set notebook style

#%load_ext autoreload
#%autoreload 2
from IPython.display import display, HTML

css = """
<style>
div.input_area {
    overflow: hidden !important; /* Hide the whole input area */
    line-height: 1em; /* Define a height for one line */
    max-height: 3.5em; /* Show only the first line */
}
</style>
"""
display(HTML(css))
# %% 
