import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name="nng_sdk",
        version="1.2.15",
        description="Software Development Kit for nng services",
        author="Alonas Collective",
        packages=setuptools.find_packages(),
        install_requires=[
            "pydantic<3.0.0",
            "vk-api",
            "onepasswordconnectsdk",
            "requests",
            "psycopg[binary]",
            "sqlalchemy==2.0.27",
        ],
    )
