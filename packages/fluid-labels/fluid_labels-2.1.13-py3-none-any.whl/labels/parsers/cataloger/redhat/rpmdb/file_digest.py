from pydantic import BaseModel


class DigestAlgorithm(BaseModel):
    algorithm: int

    def __str__(self) -> str:
        return self.get_algorithm_name()

    def get_algorithm_name(self) -> str:
        return {
            1: "md5",
            2: "sha1",
            3: "ripemd160",
            5: "md2",
            6: "tiger192",
            7: "haval-5-160",
            8: "sha256",
            9: "sha384",
            10: "sha512",
            11: "sha224",
        }.get(self.algorithm, "unknown-digest-algorithm")
