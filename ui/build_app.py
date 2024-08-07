from app import app, freezer

# Generate the map before freezing
with app.app_context():
    app.test_client().get('/')

if __name__ == '__main__':
    freezer.freeze()