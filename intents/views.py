from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import IntentSerializer, IntentTextSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Intent



class IntentCreateView(APIView):
    def post(self, request, format=None):
        intent_serializer = IntentSerializer(data=request.data)
        if intent_serializer.is_valid():
            intent = intent_serializer.save()

            intent_texts_data = request.data.get('intent_texts', [])
            for language_data in intent_texts_data:
                language_data['intent'] = intent.pk  # Set the intent field to the created intent ID
                intent_text_serializer = IntentTextSerializer(data=language_data)
                if intent_text_serializer.is_valid():
                    intent_text_serializer.save()
                else:
                    return Response(intent_text_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(intent_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(intent_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IntentListView(ListAPIView):
    queryset = Intent.objects.all()
    serializer_class = IntentSerializer

class IntentDetailView(APIView):
    def get_object(self, pk):
        try:
            return Intent.objects.get(pk=pk)
        except Intent.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        try:
            intent = self.get_object(pk)
            serializer = IntentSerializer(intent)
            return Response(serializer.data)
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk, format=None):
        try:
            intent = self.get_object(pk)
            serializer = IntentSerializer(intent, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk, format=None):
        try:
            intent = self.get_object(pk)
            serializer = IntentSerializer(intent, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk, format=None):
        try:
            intent = self.get_object(pk)
            intent.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
