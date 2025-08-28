from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader, meta
import importlib.resources
from shirotsubaki.style import Style
from shirotsubaki.element import Element as Elm
import os


class ReportBase(ABC):
    @abstractmethod
    def __init__(self, title=None) -> None:
        template_dir = importlib.resources.files('shirotsubaki').joinpath('templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.style = Style.default()
        self._data = {}
        self.keys_list = []
        self.keys_reserved = ['style']
        if title is not None:
            self.set('title', title)

    def set(self, key, value) -> None:
        if (key in self.keys_reserved) or (key in self.keys_list):
            print(f'Key \'{key}\' is not allowed to be set.')
            return
        self._data[key] = value

    def append_to(self, key, value) -> None:
        if key not in self.keys_list:
            print(f'Key \'{key}\' is not allowed to be append.')
            return
        self._data[key].append(value)

    @abstractmethod
    def append(self, value) -> None:
        pass

    def output(self, out_html: str, verbose: bool =True) -> None:
        """Output the report.

        Args:
            out_html: Path to the output file
            verbose: Whether to print the output file path and file size to stdout
        """
        self._data['style'] = str(self.style)
        for key in self.keys_list:
            self._data[key] = '\n'.join([str(v) for v in self._data[key]])
        with open(out_html, 'w', encoding='utf8', newline='\n') as ofile:
            ofile.write(self.template.render(self._data))
        if verbose:
            print(f'{out_html} ({(os.path.getsize(out_html) / 1024):.2f} KB)')

    def append_as_toggle(self, toggle_id, content, message='Show details'):
        self.style.set(f'#toggle{toggle_id}', 'display', 'none')
        self.style.set(f'.content{toggle_id}', 'display', 'none')
        self.style.set(f'#toggle{toggle_id}:checked ~ .content{toggle_id}', 'display', 'block')
        self.style += Style({
            'label.toggle-label': {
                'display': 'inline-block',
                'color': 'var(--text-link)',
                'margin-bottom': '1.0em',
            },
        })
        self.style.set('div.toggle-area', 'background', 'var(--surface-primary)')
        self.style.set('div.toggle-area', 'padding', '1.0em')
        label = Elm('label', message)
        label.set_attr('for', f'toggle{toggle_id}')
        label.set_attr('class', 'toggle-label')
        self.append(label)
        self.append(Elm('input').set_attr('type', 'checkbox').set_attr('id', f'toggle{toggle_id}'))
        self.append(Elm('div', content).set_attr('class', f'toggle-area content{toggle_id}'))
        self.append('<br/>')

    def append_as_minitabs(self, tabs_id: str, contents: dict, tabs_per_line: int = 0):
        self.style.set(', '.join([
            f'#tabs{tabs_id}-btn{i_tab:04d}:checked ~ #tabs{tabs_id}-content{i_tab:04d}'
            for i_tab in range(len(contents))
        ]), 'display', 'block')
        selectors_has = ', '.join([
            f':has(#tabs{tabs_id}-btn{i_tab:04d}:checked) label[for="tabs{tabs_id}-btn{i_tab:04d}"]'
            for i_tab in range(len(contents))
        ])
        self.style += Style({
            selectors_has: {'background': 'var(--surface-secondary)', 'color': '#ffffff'},
        })
        self.style += Style({
            '.tab-content': {'display': 'none', 'margin-bottom': '1.0em'},
        })
        self.style += Style.tab_label()
        for i_tab, tab_name in enumerate(contents.keys()):
            id_ = f'tabs{tabs_id}-btn{i_tab:04d}'
            checked = 'checked' if (i_tab == 0) else ''
            label = Elm('label', tab_name).set_attr('class', 'tab-label')
            label.set_attr('for', id_)
            self.append(label)
            self.append(f'<input type="radio" name="tabs{tabs_id}" id="{id_}" hidden {checked}/>')
            if tabs_per_line >= 1: 
                if (i_tab + 1) % tabs_per_line == 0:
                    self.append('<br/>')
        for i_tab, content in enumerate(contents.values()):
            id_ = f'tabs{tabs_id}-content{i_tab:04d}'
            self.append(Elm('div', content).set_attr('id', id_).set_attr('class', 'tab-content'))


class Report(ReportBase):
    """A class for creating a simple report.

    Args:
        title: HTML title (can also be set later)

    Example:
        ```python
        import shirotsubaki.report
        from shirotsubaki.element import Element as Elm

        rp = shirotsubaki.report.Report(title='Fruits')
        rp.style.set('h1', 'color', 'steelblue')
        rp.append(Elm('h1', 'Fruits Fruits'))
        rp.append('Fruits Fruits Fruits')
        rp.output('docs/example_report.html')
        ```

        [example_report.html](../example_report.html)
    """
    def __init__(self, title: str = None) -> None:
        super().__init__(title)
        self.template = self.env.get_template('report.html')
        self._data['content'] = []
        self.keys_list.append('content')

    def append(self, value) -> None:
        self.append_to('content', value)


class ReportWithTabs(ReportBase):
    """A class for creating a report with tabs.

    Args:
        title: HTML title that also serves as the report heading (can also be set later)

    Example:
        ```python
        import shirotsubaki.report

        rp = shirotsubaki.report.ReportWithTabs()
        rp.set('title', 'Fruits Fruits Fruits')
        rp.add_tab('apple', 'apple apple')
        rp.add_tab('banana', 'banana banana')
        rp.add_tab('cherry', 'cherry cherry')
        rp.output('docs/example_report_with_tabs.html')
        ```

        [example_report_with_tabs.html](../example_report_with_tabs.html)
    """
    def __init__(self, title: str = None) -> None:
        super().__init__(title)
        self.template = self.env.get_template('report_with_tabs.html')
        self.style += Style({
            'body': {
                'margin': '0',
                'padding-top': '10em',
            },
            '.header': {
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'background': '#ffffff',
                'z-index': '100',
                'padding': '10px 20px 5px',
                'border-bottom': '1px solid var(--text-primary)',
                'width': '100%',
            },
            '.tab': {
                'margin': '20px',
                'display': 'none',
            },
        })
        self.style += Style.tab_label()

        self.tabs = {}
        self.current_tab = None
        self.keys_reserved.append('tabs')

    def add_tab(self, tabname: str, content: str | Elm = None) -> None:
        """Add a tab to the report.

        Args:
            tabname: The name of the tab (this will be displayed on the tab)
            content: The content to be placed in the tab (can also be added later)
        """
        if tabname in self.tabs:
            raise KeyError(f'Tab \'{tabname}\' already exists.')
        self.tabs[tabname] = [content] if content else []
        self.current_tab = tabname

    def append_to_tab(self, tabname: str, value) -> None:
        if tabname not in self.tabs:
            self.add_tab(tabname)
        self.tabs[tabname].append(value)

    def switch_tab(self, tabname) -> None:
        self.current_tab = tabname

    def append(self, value) -> None:
        self.append_to_tab(self.current_tab, value)

    def _create_elements(self) -> None:
        selectors_comb = []
        selectors_has = []
        elements_radio = []
        elements_label = []
        for i, label in enumerate(self.tabs):
            selectors_comb.append(f'#btn{i:02}:checked ~ #tab{i:02}')
            selectors_has.append(f':has(#btn{i:02}:checked) .header label[for="btn{i:02}"]')
            elements_radio.append(f'<input type="radio" name="tab" id="btn{i:02}" hidden/>')
            elements_label.append(f'<label for="btn{i:02}" class="tab-label">{label}</label>')
        elements_radio[0] = elements_radio[0].replace('hidden', 'hidden checked')
        self.style += Style({',\n'.join(selectors_comb): {'display': 'block'}})
        selectors_has = ',\n'.join(selectors_has)
        self.style += Style({
            selectors_has: {'background': 'var(--surface-secondary)', 'color': '#ffffff'},
        })
        self.set('elements_radio', '\n'.join(elements_radio))
        self.set('elements_label', '\n'.join(elements_label))

    def output(self, out_html) -> None:
        self._create_elements()
        for tabname in self.tabs:
            self.tabs[tabname] = '\n'.join([str(v) for v in self.tabs[tabname]])
        self._data['tabs'] = self.tabs
        super().output(out_html)
