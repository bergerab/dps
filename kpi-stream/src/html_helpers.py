from yattag import Doc

def table(doc, header, rows=[[]]):
    if len(rows) == 0 or len(rows) == 1 and len(rows[0]) == 0:
        with doc.tag('i'):
            doc.text('None')
        return
    with doc.tag('table', klass='pretty'):
        for item in header:
            with doc.tag('th'):
                doc.text(item)
        for row in rows:
            with doc.tag('tr'):
                for item in row:
                    with doc.tag('td'):
                        doc.asis(item)

def render_page(child_doc, notifications=None, errors=None):
    if not notifications:
        notifications = []
    if not errors:
        errors = []
    doc, tag, text = Doc().tagtext()
    doc.asis('<!DOCTYPE HTML>')
    with tag('html', lang='en'):
        with tag('head'):
            doc.stag('meta', charset='UTF-8')
            with tag('title'):
                text('METER Control Panel')
            doc.stag('meta', name='description', content='Frontend for running HIL Simulations')
            doc.stag('meta', name='author', content='UWM')            
        with tag('body'):
            with tag('div', klass='header'):
                a(doc, 'METER Control Panel', '/', style='font-size: 20pt;')
                with tag('div', klass='nav'):
                    navitem(doc, 'Overview', '/')                    
                    navitem(doc, 'Simulate', '/stream')
                    navitem(doc, 'Batch Process', '/batch')                    
                    navitem(doc, 'Visualize', '/visualize')
                    navitem(doc, 'Load Data', '/load')
                    navitem(doc, 'Maintenance', '/database')                    
            with tag('div', id='content'):
                if notifications:
                    with doc.tag('div', klass='info'):
                        with doc.tag('div', style='padding: 10px 10px 0 10px;'):
                            text('System notification:')
                        with doc.tag('ul'):
                            for notification in notifications:
                                with doc.tag('li'):
                                    text(notification)
                if errors:
                    with doc.tag('div', klass='error'):
                        with doc.tag('div', style='padding: 10px 10px 0 10px;'):
                            text('One or more errors have occured:')
                        with doc.tag('ul'):
                            for error in errors:
                                with doc.tag('li'):
                                    text(error)
                                    
                doc.asis(child_doc.getvalue())
                                    

            with tag('style'):
                doc.asis('''
html, body {
                height: 100%;
}
                
body {
                font-family: arial;
                margin: 0;

                background: #efefef;
}

#content {
                margin-left: 20px;
                margin-right: 20px;
}

.checkbox-label {
                font-size: 10pt;
}
                
input[type=button], input[type=submit],                                
a.button {
                display: inline-block;
                padding: 10px 15px;
                text-decoration: none;
                border: 0px solid gray;
                color: white;
                user-select: none;
                font-size: 10pt;
                font-weight: bold;
                text-transform: uppercase;
                border-radius: 5px;
                background: #3f51b5;
                font-family: "Roboto", "Helvetica", "Arial", sans-serif;
                box-shadow: 0px 3px 1px -2px rgba(0,0,0,0.2),0px 2px 2px 0px rgba(0,0,0,0.14),0px 1px 5px 0px rgba(0,0,0,0.12);
}

input[type=button]:hover, input[type=submit]:hover,                
a.button:hover {
                transition: 0.5s;
                box-shadow: 0px 2px 4px -1px rgba(0,0,0,0.2),0px 4px 5px 0px rgba(0,0,0,0.14),0px 1px 10px 0px rgba(0,0,0,0.12);
                background: #303f9f;
                cursor: pointer;
}

input[type=button]:focus, input[type=submit]:focus,                
a.button:focus {
                border: 1px solid darkgray;
}


                

.header {
                font-size: 24pt;
                font-weight: bold;
                
                padding-left: 20px;
                padding-top: 10px;
                
                margin-bottom: 10px;

                background: #3f51b5;
                color: white;

                box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
}

.header a {
                color: white;
}

.header > a:first-child {
                text-decoration: none;
}
                
.info {
                padding: 10px;
                color: #0000ffdd;
                background: white;
                box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
                margin-bottom: 10px;
}

.error {
                padding: 10px;
                color: #ff0000dd;
                background: white;
                box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
                margin-bottom: 10px;
}

.box {
                background: white;
                margin-bottom: 20px;
                box-shadow: 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23);
                padding: 5px;
}

.box-header {
                font-size: 18pt;
                font-weight: bold;
                padding: 10px;
}

.box-body {
                padding: 10px;
}

table.pretty {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

table.pretty td, table.pretty th {
  border: 1px solid #ededed;
  text-align: left;
  padding: 8px;
}

table.pretty tr:nth-child(even) {
  background-color: #ededed;
}

table.pretty th {
                text-align: left;
}

table.pretty td {
                white-space: pre-line;
}

.buttons > * {
                margin-right: 10px;
}

.nav {
                margin-left: 10px;
                padding-bottom: 20px;
                margin-top: 20px;
                font-size: 12pt;
}
                
.nav > .navitem {
                margin-right: 10px;
                padding: 10px;
                text-decoration: none;
                font-weight: normal;                
}

.ftable-label {
                text-align: right;
                padding-right: 20px;
}

.ftable > tr {
                margin-bottom: 10px;
}

.row {
                margin-bottom: 10px;
}

.navitem:hover {
                background: #303f9f;
                transition: background 0.5s;
                border-radius: 20px;
}

.help {
                border: 1px solid gray;
                border-radius: 20px;
                color: gray;
                padding: 2pt 4pt;
                transition: background 0.5s;
                font-size: 8pt;
                margin-left: 10px;
}

.help:hover {
                background: #efefef;
                cursor: help;
}

.help-text {
                display: none;
                position: absolute;
                background: black;
                color: white;
                opacity: 0.8;
                padding: 20px;
                font-size: 10pt;
                white-space: pre-line;
}
                ''')
                
            with doc.tag('script'):
                doc.asis('''
                var helps = document.getElementsByClassName('help');

                for (let i=0; i < helps.length; ++i) {
                    var help = helps[i];
                    help.addEventListener('mouseenter', function () {
                        helps[i].children[0].style.display = 'inline-block';
                    });
                
                    help.addEventListener('mouseleave', function () {
                        helps[i].children[0].style.display = 'none';
                    });
                }

                ''')
        
                
    return doc.getvalue()

def a(doc, text, href, **kwargs):
    with doc.tag('a', href=href, **kwargs):
        doc.text(text)

def button(doc, text, href, **kwargs):
    with doc.tag('a', href=href, klass='button', **kwargs):
        doc.text(text)
        
def div(doc, k):
    with doc.tag('div'):
        k()

def title(doc, text):
    with doc.tag('h2'):
        doc.text(text)

def error(doc, text):
    with doc.tag('div', klass='error'):
        doc.text(text)

def info(doc, text):
    with doc.tag('div', klass='info'):
        doc.text(text)
        
def quote(x):
    return '"%s"' % x

def navitem(doc, name, href, **kwargs):
    with doc.tag('a', href=href, klass='navitem', **kwargs):
        doc.text(name)

def ftable(doc, items):
    with doc.tag('table'):
        for i in range(len(items)):
            with doc.tag('tr'):
                x, y = items[i]
                if x == 'asis':
                    with doc.tag('td', style='width 100%;'):
                        y(doc)
                    continue
                
                with doc.tag('td', klass='ftable-label'):
                    doc.text(str(x))
                with doc.tag('td'):
                    y(doc)

def help(doc, text):
    with doc.tag('span', klass='help'):
        doc.text('?')
        with doc.tag('span', klass='help-text'):
            doc.text(text)
