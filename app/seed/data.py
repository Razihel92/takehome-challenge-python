from app.users.schemas import UserCreateSchema

SEED_USERS: list[UserCreateSchema] = [
    UserCreateSchema(
        username="ash",
        email="ash@pokemon.com",
        password="pikachu123",
        pokemon_ids=[25, 6, 1],
        items_ids=[1, 4],
    ),
    UserCreateSchema(
        username="misty",
        email="misty@pokemon.com",
        password="starmie123",
        pokemon_ids=[120, 121, 54],
        items_ids=[2, 3],
    ),
    UserCreateSchema(
        username="brock",
        email="brock@pokemon.com",
        password="onix1234",
        pokemon_ids=[74, 95],
        items_ids=[4],
    ),
    UserCreateSchema(
        username="gary",
        email="gary@pokemon.com",
        password="blastoise123",
        pokemon_ids=[9, 59, 65],
        items_ids=[24, 28],
    ),
    UserCreateSchema(
        username="jessie",
        email="jessie@teamrocket.com",
        password="arbok1234",
        pokemon_ids=[23, 24, 52],
        items_ids=[17],
    ),
    UserCreateSchema(
        username="james",
        email="james@teamrocket.com",
        password="weezing123",
        pokemon_ids=[109, 110],
        items_ids=[26],
    ),
    UserCreateSchema(
        username="dawn",
        email="dawn@pokemon.com",
        password="piplup1234",
        pokemon_ids=[393, 417],
        items_ids=[17, 25],
    ),
    UserCreateSchema(
        username="may",
        email="may@pokemon.com",
        password="torchic123",
        pokemon_ids=[255, 300],
        items_ids=[26],
    ),
    UserCreateSchema(
        username="serena",
        email="serena@pokemon.com",
        password="fennekin123",
        pokemon_ids=[653],
        items_ids=[29],
    ),
    UserCreateSchema(
        username="erika",
        email="erika@pokemon.com",
        password="vileplume123",
        pokemon_ids=[45, 114],
        items_ids=[23, 17],
    ),
]
