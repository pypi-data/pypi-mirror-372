from piprints.main.models import Paper, Person, User, Tag, Keyword
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username', )

class PersonSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Person
        fields = (
            'id',
            'lastname',
            'firstname',
            'affiliation',
            'user', )

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('value', )

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = ('name', )

class PaperSerializer(serializers.ModelSerializer):
    authors = PersonSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    keywords = KeywordSerializer(many=True, read_only=True)
    class Meta:
        model = Paper
        fields = (
            'id',
            'title',
            'authors',
            'year',
            'journal',
            'number',
            'pages',
            'abstract',
            'notes',
            'keywords',
            'tags', )
