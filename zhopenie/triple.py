# -*- coding: utf-8 -*-
class Entity():

    def __init__(self, type=None, content=[], loc=0):
        self.type = type
        self.content = content
        self.loc = loc

    def get_content_as_str(self):
        return ''.join(self.content)

    def __str__(self):
        return 'type:{}, content:{}'.format(self.type, self.content)


class Relation():

    def __init__(self, content=[]):
        self.content = content

    def get_content_as_str(self):
        return ''.join(self.content)

    def __str__(self):
        return 'content:{}'.format(self.content)

class Triple():

    def __init__(self, entity_1=Entity(), entity_2=Entity(), relation=Relation()):
        self.entity_1 = entity_1
        self.entity_2 = entity_2
        self.relation = relation

    def __str__(self):
        try:
            return 'e1:{}, e2:{}, r:{}'.format(''.join(self.entity_1.content), ''.join(self.entity_2.content), self.relation.content)
        except:
            return 'Error occurred in toString() method!'
