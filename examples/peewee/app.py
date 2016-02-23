import argparse
import peewee as pw
import autobahn_sync


try:
    input = raw_input
except:  # Except if we use Python3
    pass


def startup_library_service():
    wamp = autobahn_sync.AutobahnSync()
    wamp.run()
    db = pw.SqliteDatabase('books.db')

    class Book(pw.Model):
        title = pw.CharField()
        author = pw.CharField()

        class Meta:
            database = db

    try:
        db.create_table(Book)
    except pw.OperationalError:
        pass

    @wamp.register('com.library.get_book')
    def get_book(id):
        try:
            b = Book.get(id=id)
        except pw.DoesNotExist:
            return {'_error': "Doesn't exist"}
        return {'id': id, 'title': b.title, 'author': b.author}

    @wamp.register('com.library.new_book')
    def new_book(title, author):
        book = Book(title=title, author=author)
        book.save()
        wamp.session.publish('com.library.book_created', book.id)
        return {'id': book.id}


class Repl(object):

    USAGE = """help: print this message
new: create a book
get <book_id>: retrieve a book
quit: leave the console"""

    def __init__(self):
        # Create another autobahn
        self.wamp = autobahn_sync.AutobahnSync()
        self.wamp.run()

        @self.wamp.subscribe('com.library.book_created')
        def on_book_created(book_id):
            print('[Event] Someone else has created book %s' % book_id)

    def get_book(self, id):
        result = self.wamp.session.call('com.library.get_book', id)
        if '_error' in result:
            print('Error: %s' % result['_error'])
        else:
            print('Found book %s' % result)

    def new_book(self):
        title = input('Title ? ')
        author = input('Author ? ')
        result = self.wamp.session.call('com.library.new_book', title, author)
        if '_error' in result:
            print('Error: %s' % result['_error'])
        else:
            print('Created book %s' % result['id'])

    def start(self):
        quit = False
        print("Welcome to the book shell, type `help` if you're lost")
        while not quit:
            cmd = input('> ')
            cmd = cmd.strip()
            if cmd == 'help':
                print(self.USAGE)
            elif cmd.startswith("new"):
                self.new_book()
            elif cmd.startswith("get"):
                self.get_book(cmd.split()[1:])
            elif cmd == 'quit':
                quit = True
            else:
                print('Error: Unknow command !')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Small demo of Autobahn & Peewee app')
    parser.add_argument('--repl', action='store_true',
                        help='Only start the REPL loop console')
    parser.add_argument('--library', action='store_true',
                        help='Only start the book storage service')
    args = parser.parse_args()
    # Check if the two arguments are not both disabled or both enabled
    start_both = not (args.library ^ args.repl)
    if args.library or start_both:
        startup_library_service()
        if not start_both:
            # Start infinite loop and wait
            print("Library lanched, hit ^C to stop.")
            from time import sleep
            while True:
                sleep(1)
    if args.repl or start_both:
        repl = Repl()
        repl.start()
