from dash import html, clientside_callback, Output, Input, State, MATCH
import dash_bootstrap_components as dbc
import uuid

HTML2CANVAS_URL = {'src': 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'}


class DownloadImageAIO(html.Div):

    class ids:
        button = lambda aio_id: {
            'component': 'DownloadImageAIO',
            'subcomponent': 'button',
            'aio_id': aio_id
        }
        dom_id = lambda aio_id: {
            'component': 'DownloadImageAIO',
            'subcomponent': 'dom_id',
            'aio_id': aio_id
        }
        dummy = lambda aio_id: {
            'component': 'DownloadImageAIO',
            'subcomponent': 'dummy',
            'aio_id': aio_id
        }
    ids = ids

    def __init__(
        self,
        dom_id=None,
        aio_id=None,
        className='',
        button_class_name='',
        text='Download'
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        
        button = [
            dbc.Button([
                    html.I(className='fas fa-download', title='Download image (png)'),
                    html.Span(text, className='ms-1 d-sm-inline-block d-none') if text else ''
                ],
                id=self.ids.button(aio_id),
                n_clicks=0,
                class_name=button_class_name
            ),
            dbc.Input(id=self.ids.dom_id(aio_id), value=dom_id, class_name='d-none'),
            html.Div(id=self.ids.dummy(aio_id))
        ]
        super().__init__(button, className=className)

    clientside_callback(
        '''
        function (clicks, id) {
          const today = new Date();
          const dateString = today.toISOString().substring(0, 10);
          fileName = `trainerhill-${id}-${dateString}.png`;
          if (clicks > 0) {
            html2canvas(document.getElementById(id), { useCORS: true, backgroundColor: '#ffffff' }).then(function (canvas) {
              var anchorTag = document.createElement('a');
              anchorTag.download = fileName;
              anchorTag.href = canvas.toDataURL('image/png');
              anchorTag.target = '_blank';
              document.body.appendChild(anchorTag);
              anchorTag.click();
              document.body.removeChild(anchorTag);
            })
        }
        ''',
        Output(ids.dummy(MATCH), 'className'),
        Input(ids.button(MATCH), 'n_clicks'),
        State(ids.dom_id(MATCH), 'value'),
    )
