from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=False, write_only=True)
    code = serializers.CharField(required=False)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        code = data.get('code')

        if (email and not password) or (password and not email):
            raise serializers.ValidationError("Si se proporciona email, también debe proporcionarse password")
        
        if not (email and password) and not code:
            raise serializers.ValidationError("Debe proporcionar email y password, o code")

        return data 