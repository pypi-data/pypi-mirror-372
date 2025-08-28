import os
import jwt
import secrets
import time
import bcrypt
import json
import argparse


class UserGenerator:
    def __init__(self, secret_key: str, username: str, password: str):
        """
        Initialize the Authen class with a secret key for JWT signing.

        Args:
            secret_key: The key used for signing/verifying JWTs (string).
        """
        self.secret_key = secret_key
        self.algorithm = "HS256"  # Default to HMAC SHA-256
        # Supported algorithms in PyJWT
        self.supported_algorithms = ["HS256", "HS384", "HS512"]
        self.username = username
        self.password = password

    @classmethod
    def from_config(cls, config_path: str = "authen/secret.json"):
        """
        Initialize UserGenerator instance from a JSON configuration file.

        Args:
            config_path: Path to the JSON configuration file (default: authen/secret.json).
        Returns:
            An instance of UserGenerator with values loaded from the config file.
        Raises:
            FileNotFoundError: If the config file doesn't exist.
            KeyError: If required fields are missing in the config file.
            json.JSONDecodeError: If the config file is invalid JSON.
        """
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            required_fields = ["secret_key", "username", "password"]
            missing_fields = [field for field in required_fields if field not in config]
            if missing_fields:
                raise KeyError(f"Missing required fields in config: {missing_fields}")

            return cls(
                secret_key=config["secret_key"],
                username=config["username"],
                password=config["password"],
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in config file: {e}", e.doc, e.pos
            )

    @staticmethod
    def generate_secret_key() -> str:
        """
        Generate a random secret key for JWT signing.

        Returns:
            A secure random string suitable for HS256 signing.
        """
        return secrets.token_hex(32)

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: The plaintext password to hash.
        Returns:
            The hashed password as a string.
        """
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def encrypt(
        self,
        secret_key: str = "",
        algorithm: str = "HS256",
        seconds_to_expire: int = 3600,
    ) -> str:
        """
        Encode a hashed username/password into a JWT using the specified algorithm.

        Args:
            secret_key: The secret key for signing the JWT.
            algorithm: The signing algorithm (e.g., 'HS256'). Defaults to HS256.
        Returns:
            The encoded JWT as a string.
        Raises:
            ValueError: If the algorithm is not supported.
            RuntimeError: If encoding fails.
        """
        if algorithm not in self.supported_algorithms:
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. Supported: {self.supported_algorithms}"
            )

        try:
            self.hashed_password = self.hash_password(self.password)
            payload = {
                "hashed_password": self.hashed_password,
                "exp": int(time.time()) + seconds_to_expire,  # Expire in 1 hour
                "iat": int(time.time()),  # Issued at
            }
            signing_key = secret_key or self.secret_key
            self.token = jwt.encode(payload, signing_key, algorithm=algorithm)
            return self.token
        except Exception as e:
            raise RuntimeError(f"Failed to encode JWT: {e}") from e

    def decode_token(self, token: str, secret_key: str = None) -> str:
        """
        Decode and verify a JWT to extract the hashed password.

        Args:
            token: The encoded JWT string.
            secret_key: The secret key used for decoding the JWT.
        Returns:
            The hashed password from the JWT payload.
        Raises:
            ValueError: If the schema is not supported.
            RuntimeError: If decoding/verification fails (e.g., invalid token or key).
        """
        if self.algorithm not in self.supported_algorithms:
            raise ValueError(
                f"Unsupported schema: {self.algorithm}. Supported: {self.supported_algorithms}"
            )

        try:
            if secret_key:
                payload = jwt.decode(token, secret_key, algorithms=[self.algorithm])
            else:
                payload = jwt.decode(
                    token, self.secret_key, algorithms=[self.algorithm]
                )
            return payload["hashed_password"]
        except jwt.InvalidTokenError as e:
            raise RuntimeError(f"Failed to decode JWT: {e}") from e

    def verify_password(self, hashed_password: str, password: str = "") -> bool:
        """
        Verify a password against a hashed password.

        Args:
            hashed_password: The hashed password to compare against.
            password: The password to verify.
        Returns:
            True if the password matches, False otherwise.
        """
        actual_password = password or self.password
        return bcrypt.checkpw(
            actual_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def save_authorization(self, save_path: str = "authen/secret.json"):
        """
        Save authorization details to a JSON file.
        Args:
            save_path: The path to save the JSON
        """
        if not os.path.exists("authen"):
            os.makedirs("authen")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "w") as f:
            auth = {
                "secret_key": self.secret_key,
                "username": self.username,
                "password": self.password,
                "hashed_password": self.hashed_password,
                "algorithm": self.algorithm,
                "token": self.token,
                "api_url": "http://localhost:8000/verify-token",
            }
            json.dump(auth, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="User authentication with JWT and bcrypt"
    )
    parser.add_argument(
        "--save_path",
        default="authen/secret.json",
        help="Path to save the authorization JSON file",
    )
    args = parser.parse_args()

    # Generate a secret key
    secret_key = UserGenerator.generate_secret_key()

    # Initialize
    auth = UserGenerator(secret_key=secret_key, username="Kan", password="password123")
    print(f"- Username: {auth.username}\n- Password: {auth.password}")

    # Sign a new JWT token
    token = auth.encrypt()
    print(f"- JWT: {token}")

    # Decode JWT to get hashed password
    hashed_password = auth.decode_token(token=token)
    print(f"- Hashed password: {hashed_password}")

    # Verify original password
    is_valid = auth.verify_password(hashed_password, "password123")
    print(f"- Password valid: {is_valid}")

    # Save authorization
    auth.save_authorization(args.save_path)
