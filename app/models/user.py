# [START custom_class_def]
# [START firestore_data_custom_type_definition]
class User(object):
    def __init__(self, id, role, token=''):
        self.id = id
        self.role = role
        self.token = token

    @staticmethod
    def from_dict(id, source):
        # [START_EXCLUDE]
        user = User(id, source[u'role'])

        if u'token' in source:
            user.token = source[u'token']

        return user
        # [END_EXCLUDE]

    def to_dict(self):
        # [START_EXCLUDE]
        dest = {
            u'id': self.id,
            u'role': self.role
        }

        if self.token:
            dest[u'token'] = self.token

        return dest
        # [END_EXCLUDE]

    def __repr__(self):
        return (
            f'User(\
                id={self.id}, \
                token={self.token}, \
                role={self.role}\
            )'
        )
# [END firestore_data_custom_type_definition]
# [END custom_class_def]