from trustedauthority.app.config.settings import settings
from crypto.key import new_public_private_key_pair


def create_key_pairs():
    public_key_str, private_key_str = new_public_private_key_pair()
    public_key_file = settings.TA_PUBLIC_KEY_FILE
    private_key_file = settings.TA_PRIVATE_KEY_FILE

    with open(public_key_file, "w") as pubf:
        pubf.write(public_key_str)

    with open(private_key_file, "w") as privf:
        privf.write(private_key_str)


if __name__ == '__main__':
    create_key_pairs()
