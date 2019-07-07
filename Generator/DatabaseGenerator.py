
class DatabaseGenerator(object):
    def __init__(self, shaper_config, project_path):
        self._shaper_config = shaper_config
        self._project_path = project_path
        self._database = shaper_config.get_database()
        self._table = shaper_config.get_table()
        self._feature_count = shaper_config.get_feature_count()
        self._file_path = "/home/" + str(shaper_config.get_ssh_user()) + "/data/small_dataset.csv"

    def create_postgres_scheme(self):
        scheme = []
        scheme.append("\c " + str(self._database) + ";")
        scheme.append("CREATE TABLE " + str(self._table))
        scheme.append("(")
        counter = 0
        while counter < self._feature_count:
            if counter == self._feature_count - 1:
                scheme.append("feature" + str(counter) + " INTEGER")
            else:
                scheme.append("feature" + str(counter) + " INTEGER,")
            counter = counter + 1
        scheme.append(")")
        self.export_file(scheme, self._project_path)

    def create_mysql_scheme(self):
        scheme = []
        scheme.append("#!/bin/bash")
        scheme.append("GRANT ALL PRIVILEGES ON *.* TO \'" + str(
            self._shaper_config.get_user()) + "\'@\'%\' IDENTIFIED BY \'" + str(
            self._shaper_config.get_password()) + "\' WITH GRANT OPTION;")

        scheme.append("GRANT ALL PRIVILEGES ON *.* TO \'" + str(
            self._shaper_config.get_user()) + "\'@\'database\' IDENTIFIED BY \'" + str(
            self._shaper_config.get_password()) + "\' WITH GRANT OPTION;")
        scheme.append("FLUSH PRIVILEGES;")
        scheme.append("USE " + str(self._database) + ";")
        scheme.append("CREATE TABLE " + str(self._table))
        scheme.append("(")
        counter = 0
        while counter < self._feature_count:
            if counter == self._feature_count - 1:
                scheme.append("feature" + str(counter) + " INTEGER")
            else:
                scheme.append("feature" + str(counter) + " INTEGER,")
            counter = counter + 1
        scheme.append(")")
        self.export_file(scheme, self._project_path)

    def export_file(self, data, path):
        with open(path + "/db/init/setup.sql", 'w') as f:
            for line in data:
                f.write(line + "\n")
        f.close()




