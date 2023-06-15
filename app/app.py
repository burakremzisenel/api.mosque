#!/usr/bin/env python
from config import app
from controllers.documented import blueprint as doc_endpoint
'''
from controllers.default import blueprint as default_endpoint
'''
from controllers.basic import blueprint as basic_endpoint

# register the api
app.register_blueprint(doc_endpoint)
'''app.register_blueprint(default_endpoint)'''
app.register_blueprint(basic_endpoint)

if __name__ == '__main__':
    ''' run application '''
    app.run(host='0.0.0.0', port=5000)
#ssl_context='adhoc'