# Examples

Here are some examples of how to use this package:


### Example 1 (scrollable table)

<a href="../example_1.html" class="asis" target="_blank" rel="noopener noreferrer">example_1.html</a>

```python
import shirotsubaki.report
from shirotsubaki.element import Element as Elm

def example_1():
    rp = shirotsubaki.report.ReportWithTabs()
    rp.set('title', 'Fruits Fruits Fruits')
    rp.style.add_scrollable_table()

    rp.add_tab('apple')
    rp.append(Elm.table_from_rows([['apple'] * 10] * 20, header=True, index=True, scrollable=True))

    rp.add_tab('banana')
    rp.append(Elm.table_from_rows([['banana'] * 10] * 20, header=True, index=False, scrollable=True))

    rp.add_tab('cherry')
    rp.append(Elm.table_from_rows([['cherry'] * 10] * 20, header=False, index=False, scrollable=True))

    rp.output('docs/example_1.html')
```


### Example 2 (toggle)

<a href="../example_2.html" class="asis" target="_blank" rel="noopener noreferrer">example_2.html</a>

```python
import shirotsubaki.report
from shirotsubaki.element import Element as Elm

def example_2():
    rp = shirotsubaki.report.Report(title='Fruits')
    rp.append(Elm('h1', 'Apple'))
    rp.append_as_toggle('001', 'This message will be collapsed inside the toggle.')
    rp.output('docs/example_2.html')
```


### Example 3 (minitabs)

<a href="../example_3.html" class="asis" target="_blank" rel="noopener noreferrer">example_3.html</a>

```python
import shirotsubaki.report
from shirotsubaki.element import Element as Elm

def example_3():
    rp = shirotsubaki.report.Report(title='Fruits')
    rp.append(Elm('h1', 'Apple'))
    rp.append_as_minitabs('001', {
        'Taro': 'Taro Taro',
        'Jiro': 'Jiro Jiro',
        'Saburo': 'Saburo Saburo',
    })
    rp.append_as_minitabs('002', {
        'Shiro': 'Shiro Shiro',
        'Goro': 'Goro Goro',
        'Rokuro': 'Rokuro Rokuro',
    })
    rp.output('docs/example_3.html')
```


### Example 4 (plot)

<a href="../example_4.html" class="asis" target="_blank" rel="noopener noreferrer">example_4.html</a>

```python
import shirotsubaki.report
from shirotsubaki.utils import figure_to_html
import matplotlib.pyplot as plt

def example_4():
    plt.rcParams['svg.fonttype'] = 'none'  # to reduce file size
    plt.rcParams['svg.hashsalt'] = ''  # to make the IDs deterministic
    plt.rcParams['font.size'] = 11

    fig, ax = plt.subplots(nrows=1, figsize=(4, 3))
    ax.plot([0, 1, 2, 3, 4], [0.7, 0.5, 0.40, 0.35, 0.3])
    ax.plot([0, 1, 2, 3, 4], [0.7, 0.6, 0.55, 0.50, 0.475])

    rp = shirotsubaki.report.Report(title='Fruits')
    rp.append(figure_to_html(fig, callback=plt.close))
    rp.output('docs/example_4.html')
```


### Example 5 (data frame)

<a href="../example_5.html" class="asis" target="_blank" rel="noopener noreferrer">example_5.html</a>

```python
import shirotsubaki.report
from shirotsubaki.utils import style_float_cols, style_top_ranks_per_row
import pandas as pd

def example_5():
    rp = shirotsubaki.report.Report(title='Fruits')

    df = pd.DataFrame({
        'Task Name': ['Task 1', 'Task 2', 'Task 3', 'Task 4'],
        'Model A Loss': [0.1, 0.3, 0.1, 0.1],
        'Model B Loss': [0.2, 0.1, 0.3, 0.1],
        'Model C Loss': [0.3, 0.2, 0.1, 0.1],
    })
    df.set_index('Task Name', inplace=True, drop=True)
    df.columns.name = 'Task Name'
    df.index.name = None

    styled = df.style
    styled = style_float_cols(styled)
    styled = style_top_ranks_per_row(styled, [col for col in df.columns if col.startswith('Model')])
    rp.append(styled.to_html())

    rp.output('docs/example_5.html')
```
