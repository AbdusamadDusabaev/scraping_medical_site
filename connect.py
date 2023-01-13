import pymysql
from pymysql import cursors
from config import port, host, db_username, password, db_name


def database(query):
    print("[INFO] Делаем SQL запрос к базе данных")
    try:
        connection = pymysql.connect(port=port, host=host, user=db_username, password=password,
                                     database=db_name, cursorclass=cursors.DictCursor)
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            connection.commit()
            print("[INFO] SQL запрос успешно выполнен")
            return result
        except Exception as ex:
            print(f"[ERROR] Something Wrong: {ex}")
            return "Error"
        finally:
            connection.close()
    except Exception as ex:
        print(f"[ERROR] Connection was not completed because {ex}")
        return "Error"


def create_table_one():
    query = "CREATE TABLE body_parts (`id` INT UNIQUE NOT NULL, `body_part` VARCHAR(100));"
    database(query=query)
    query = """INSERT INTO body_parts (`id`, `body_part`) 
               VALUES (1, 'Shoulder'), (2, 'Elbow'), (3, 'Hand'), (4, 'Hip'), (5, 'Knee'), (6, 'Foot');"""
    database(query=query)
    print("[INFO] Первая таблица создана и заполнена")


def create_table_two():
    query = "CREATE TABLE limb_parts (`id` INT UNIQUE AUTO_INCREMENT, `parent_id` INT NOT NULL, `name` VARCHAR(100));"
    database(query=query)
    query = """INSERT INTO limb_parts (`parent_id`, `name`) VALUES
               (1, 'Clavicle'), (1, 'Proximal humerus'), (1, 'Scapula'), (1, 'Humeral shaft'),
               (2, 'Shoulder'), (2, 'Humeral shaft'), (2, 'Distal humerus'), (2, 'Proximal forearm'), 
               (2, 'Forearm shaft'), (2, 'Distal forearm'),
               (3, 'Distal forearm'), (3, 'Carpal bones'), (3, 'Metacarpals'), (3, 'Thumb'), (3, 'Proximal phalanges'), 
               (3, 'Middle phalanges'), (3, 'Distal phalanges'),
               (4, 'Pelvic ring'), (4, 'Acetabulum'), (4, 'Proximal femur'), (4, 'Femoral shaft'), (4, 'Distal femur'),
               (4, 'Patella'),
               (5, 'Femoral shaft'), (5, 'Distal femur'), (5, 'Patella'), (5, 'Proximal tibia'), (5, 'Tibial shaft'),
               (5, 'Distal tibia'), (5, 'Malleoli'),
               (6, 'Calcaneus'), (6, 'Malleoli'), (6, 'Talus'), (6, 'Midfoot'), (6, 'Metatarsals'), (6, 'Phalanges');
               """
    database(query=query)


def create_table_three():
    query = """CREATE TABLE injury_groups
               (`id` INT NOT NULL UNIQUE AUTO_INCREMENT, `parent_id` INT NOT NULL, `name` VARCHAR(1000))"""
    database(query=query)


def insert_into_table_injury_groups(parent_id, name):
    query = f"""INSERT INTO injury_groups (`parent_id`, `name`) VALUES ({parent_id}, "{name}");"""
    database(query=query)


def create_table_four():
    query = """CREATE TABLE injuries (`id` INT NOT NULL UNIQUE AUTO_INCREMENT, `parent_id` INT NOT NULL, 
                                      `name` VARCHAR(1000), `description` TEXT, `image` VARCHAR(500));"""
    database(query=query)


def insert_into_table_injuries(parent_id, name, description, image):
    query = f"""INSERT INTO injuries (`parent_id`, `name`, `description`, `image`) 
                VALUES ({parent_id}, "{name}", "{description}", "{image}");"""
    database(query=query)


def create_table_five():
    query = """CREATE TABLE methods_of_treatment (`id` INT NOT NULL UNIQUE AUTO_INCREMENT, `parent_id` INT NOT NULL, 
                                                  `name` VARCHAR(1000), `skill_level` INT, `equipment` INT, 
                                                  `description` TEXT, `image` VARCHAR(500));"""
    database(query=query)


def insert_into_methods_of_treatment(parent_id, name, skill_level, equipment, description, image):
    query = f"""INSERT INTO methods_of_treatment (`parent_id`, `name`, `skill_level`, 
                                                 `equipment`, `description`, `image`)
                VALUES ({parent_id}, "{name}", {skill_level}, {equipment}, "{description}", "{image}");"""
    database(query=query)


def create_table_six():
    query = """CREATE TABLE treatment_descriptions (`id` INT NOT NULL UNIQUE AUTO_INCREMENT, `parent_id` INT NOT NULL, 
                                                    `name` VARCHAR(1000), `description` TEXT, `image` VARCHAR(500));"""
    database(query=query)


def insert_into_treatment_descriptions(parent_id, name, description, image):
    query = f"""INSERT INTO treatment_descriptions (`parent_id`, `name`, `description`, `image`)
                VALUES ({parent_id}, "{name}", "{description}", "{image}");"""
    database(query=query)


def get_injury_groups_parent_id(name):
    query = f"SELECT `id` FROM limb_parts WHERE `name` = '{name}';"
    result = database(query=query)
    return result


def get_injuries_parent_id(name):
    query = f"SELECT `id` FROM injury_groups WHERE `name` = '{name}';"
    result = database(query=query)
    return result


def get_methods_of_treatment_parent_id(name):
    query = f"SELECT `id` FROM injuries WHERE `name` = '{name}';"
    result = database(query=query)
    return result


def get_treatment_descriptions_parent_id(name):
    query = f"SELECT `id` FROM methods_of_treatment WHERE `name` = '{name}';"
    result = database(query=query)
    return result


def create_tables():
    create_table_one()
    create_table_two()
    create_table_three()
    create_table_four()
    create_table_five()
    create_table_six()


if __name__ == "__main__":
    create_tables()
