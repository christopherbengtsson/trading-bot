from dotenv.main import load_dotenv
import heroku3
import os
import json

CRYPTOS = 'CRYPTOS'
RUN_ANNA = 'RUN_ANNA'


class HerokuClient:
    def __init__(self) -> None:
        self.connect()

    def connect(self):
        self.heroku_conn = heroku3.from_key(os.environ.get('HEROKU_API_KEY'))
        self.app = self.heroku_conn.apps()['agile-oasis-43422']

    def is_authenticated(self):
        return self.heroku_conn.is_authenticated

    def restart_app(self):
        self.app.restart()

    def get_config_vars(self):
        return self.app.config()

    def start_bot(self):
        env_vars = self.get_config_vars()
        env_vars[RUN_ANNA] = 'True'

        return self.get_confirmation_config(RUN_ANNA)

    def stop_bot(self):
        env_vars = self.get_config_vars()
        env_vars[RUN_ANNA] = 'False'

        return self.get_confirmation_config(RUN_ANNA)

    def add_crypto_pair(self, value):
        env_vars = self.get_config_vars()
        existingCryptos = json.loads(env_vars[CRYPTOS])
        env_vars[CRYPTOS] = [*existingCryptos, value]

        return self.get_confirmation_config(CRYPTOS, True)

    def remove_crypto_pair(self, value):
        env_vars = self.get_config_vars()
        cryptos = json.loads(env_vars[CRYPTOS])
        cryptos.remove(value)
        env_vars[CRYPTOS] = cryptos

        return self.get_confirmation_config(CRYPTOS, True)

    def update_crypto_pair(self, fromValue, toValue):
        self.remove_crypto_pair(fromValue)
        self.add_crypto_pair(toValue)

        return self.get_confirmation_config(CRYPTOS, True)

    def get_crypto_pairs(self):
        env_vars = self.get_config_vars()
        return json.loads(env_vars[CRYPTOS])

    def get_confirmation_config(self, key, nested_key=False):
        env_vars = self.get_config_vars()

        if(nested_key):
            parsedConfig = json.loads(env_vars[key])
            return f'{key}: {str(parsedConfig)}'

        return f'{key}: {str(env_vars[key])}'


# if __name__ == '__main__':
#     # Testing Heroku Client
#     load_dotenv()
#     hc = HerokuClient()

#     print(hc.start_bot())

#     print(hc.get_crypto_pairs())
#     hc.add_crypto_pair('ATOMUSDT')
#     print(hc.get_confirmation_config(CRYPTOS))

#     hc.remove_crypto_pair('ATOMUSDT')
#     print(hc.get_confirmation_config(CRYPTOS))

#     hc.update_crypto_pair('BTCUSDT', 'ATOMUSDT')
#     print(hc.get_confirmation_config(CRYPTOS))

#     hc.update_crypto_pair('ATOMUSDT', 'BTCUSDT')
#     print(hc.get_confirmation_config(CRYPTOS))

#     # ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOTUSDT", "ENJUSDT", "AVAXUSDT", "MATICUSDT", "ILVUSDT"]
