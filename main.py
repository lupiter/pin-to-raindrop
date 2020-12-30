from raindropio import API, Collection, Raindrop
from py3pin.Pinterest import Pinterest
import sys
from time import sleep

email = sys.argv[1]
password = sys.argv[2]
username = sys.argv[3]
raindrop_access_token = sys.argv[4]

raindrop_api = API(raindrop_access_token)

pinterest = Pinterest(email=email, password=password, username=username, cred_root='.creds')
# pinterest.login()

collections = Collection.get_roots(raindrop_api)

def copy_board_section_pins(section, collection, collection_exists):
    empty = False
    while not empty:
        empty = True
        for pin in pinterest.get_section_pins(section['id']):
            empty = False
            copy_pin(pin, collection, collection_exists, section['title'])

def copy_board_pins(board_id, collection, collection_exists):
    empty = False
    while not empty:
        empty = True
        for pin in pinterest.board_feed(board_id=board_id):
            empty = False
            copy_pin(pin, collection, collection_exists)

def copy_pin(pin, collection, collection_exists, section=None):
    if pin['type'] == 'pin':
        try:
            img = pin['images']['orig']['url']
            link = pin['link'] or img
            description = pin['description']
            should_copy = True
            if collection_exists: # check for raindrop existing too
                matches = Raindrop.search(raindrop_api, collection=collection, word=link)
                for match in matches:
                    if match.link == link:
                        print(f"Skipping already copied pin: {description} link:{link} img:{img}")
                        should_copy = False
                        break
            if should_copy:
                print(f"{board_name}: Copying pin: {description} link:{link} img:{img} tagged:{section}")
                raindrop = Raindrop.create(raindrop_api, link=link, tags=[section], collection=collection, created=None, title=description, cover=img)
                print("!... wait please")
                sleep(1) # don't get rate limited by raindrop
        except KeyError:
            print(pin)
            exit(1)
    else:
        print(f"ignoring {pin['type']}")

for board in pinterest.boards_all():
    board_name = board['name']
    section = None
    collection = next((c for c in collections if c.title == board_name), None)
    collection_exists = True
    if collection == None:
        print(f"Creating collection: {board_name}")
        collection = Collection.create(raindrop_api, title=board_name)
        collection_exists = False
    else:
        print(f"Using existing collection: {board_name}")
    copy_board_pins(board['id'], collection, collection_exists)
    empty = False
    while not empty:
        empty = True
        for section in pinterest.get_board_sections(board_id=board['id']):
            copy_board_section_pins(section, collection, collection_exists)

    print(f"Done with board: {board_name}")
print(f"Done!")


pinterest.logout()
