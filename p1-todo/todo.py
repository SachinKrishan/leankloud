import datetime
import sqlite3
from flask import Flask
from flask_restplus import reqparse
from werkzeug.utils import cached_property
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix


DB_PATH = './tdo.db'  
NOTSTARTED = 'not Started'
INPROGRESS = 'in Progress'
FINISHED = 'finished'



app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
)

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'task': fields.String(required=True, description='The task details'),
    'status' : fields.String(required=True, description='The task details'),
    'due' : fields.String(required=True, description='The task details')
})

parser = reqparse.RequestParser()

class TodoDAO(object):
    def __init__(self):
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT * FROM todo")
        self.counter = len(cur.fetchall())
        self.todos = []

    def refresh(self):
        self.todos = []
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT * FROM todo")
        for ID, task, status, due in cur.fetchall():
            self.todos.append({'id':ID, 'task':task, 'status': status, 'due':due})

    def get(self, id):
        self.refresh()
        for todo in self.todos:
            if todo['id'] == id:
                return todo
        api.abort(404, "Todo {} doesn't exist".format(id))

    def create(self, data):
        todo = data
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        todo['id'] = self.counter = self.counter + 1
        cur.execute('insert into todo(id, task, status, due) values(?,?,?,?)', (todo['id'], todo['task'], todo['status'], todo['due']))
        con.commit()
        return todo

    def update(self, id, data):
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('update todo set status=? where id=?', (data['status'], id))
        con.commit()

    def delete(self, id):
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('delete from todo where id=?', (id,))
        con.commit()


    def get_due(self, due):
        self.refresh()
        dues = []
        for todo in self.todos:
            if todo['due'] == due:
                dues.append(todo)

        return dues

    def get_overdue(self):
        self.refresh()
        today = datetime.datetime.now()
        dues = []
        for todo in self.todos:
            date_str = todo['due']
            due = datetime.datetime(int(date_str[:4]), int(date_str[5:7]), int(date_str[8:]))
            if due <= today and todo['status'] != FINISHED:
                dues.append(todo)

        return dues

    def get_finished(self):
        self.refresh()
        today = datetime.datetime.now()
        fin = []
        for todo in self.todos:
            if todo['status'] == FINISHED:
                fin.append(todo)
        return fin
        





DAO = TodoDAO()
# DAO.create({'task': 'Build an API', 'due' : '2021-05-23', 'status' : "in progress"})
# DAO.create({'task': 'task 2', 'due' : '2021-05-20', 'status' : "in progress"})
# DAO.create({'task': 'profit!', 'due' : '2021-05-20', 'status' : "finished"})


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        
        DAO.refresh()
        return DAO.todos

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)

parser = reqparse.RequestParser()
parser.add_argument('due', type=str)


@ns.route('/due')
class due(Resource):
    '''gets the todos matching the date'''

    @ns.expect(parser)
    @ns.doc('get_due')
    @ns.marshal_with(todo)
    def get(self):
        '''Fetch a given resource given its due'''
        args = parser.parse_args()
        due = args['due']
        return DAO.get_due(due)

@ns.route('/overdue')
class overdue(Resource):
    '''gets the todos overdue'''

    @ns.doc('get_overdue')
    @ns.marshal_with(todo)
    def get(self):
        '''Fetch a given resource overdue'''
        return DAO.get_overdue()

@ns.route('/finished')
class finished(Resource):
    '''gets the todos finished'''

    @ns.doc('get_finished')
    @ns.marshal_with(todo)
    def get(self):
        '''Fetch a given resource finished'''
        return DAO.get_finished()

if __name__ == '__main__':
    app.run(debug=True)