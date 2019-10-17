import main

def test_create_new_profile():
    main.app.testing = True
    client = main.app.test_client()

    r = client.get('/CreateNewProfile')
