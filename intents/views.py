from django.http import Http404
from django.shortcuts import render, redirect
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import IntentSerializer, IntentTextSerializer
from .models import Intent


class IntentCreateView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'create-intent.html')

    def post(self, request, *args, **kwargs):
        intent_serializer = IntentSerializer(data=request.POST)
        if intent_serializer.is_valid():
            intent = intent_serializer.save()

            intent_texts_data = request.POST.getlist('language[]')
            raw_texts_data = request.POST.getlist('texts[]')
            print(raw_texts_data)
            texts_data = [text.split(';') for text in raw_texts_data]
            print('texts_data: ', texts_data)

            responses_data = request.POST.getlist('responses[]')
            for language, texts, responses in zip(intent_texts_data, texts_data, responses_data):
                intent_text_data = {
                    'language': language,
                    'texts': [text.strip() for text in texts],
                    'responses': [response.strip() for response in responses.split(';')],
                    'intent': intent.pk,
                }
                intent_text_serializer = IntentTextSerializer(data=intent_text_data)
                print(intent_text_serializer)
                if intent_text_serializer.is_valid():
                    intent_text_serializer.save()
                else:
                    return render(request, 'create-intent.html', {'errors': intent_text_serializer.errors})

            return redirect('create-intent')
        else:
            return render(request, 'create-intent.html', {'errors': intent_serializer.errors})


class IntentListView(APIView):
    def get(self, request, format=None):
        intents = Intent.objects.all()
        serializer = IntentSerializer(intents, many=True)
        return render(request, 'intent-list.html', {'intents': serializer.data})

class IntentDetailView(APIView):
    def get_object(self, pk):
        try:
            return Intent.objects.get(pk=pk)
        except Intent.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        try:
            intent = self.get_object(pk)
            intent_serializer = IntentSerializer(intent)
            intent_texts = intent.intent_texts.all()
            intent_texts_serializer = IntentTextSerializer(intent_texts, many=True)
            response_data = intent_serializer.data
            response_data['intent_texts'] = intent_texts_serializer.data
            return render(request, 'intent-detail.html', {'intent_data': response_data})
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk, format=None):
        try:
            intent = self.get_object(pk)
            intent.delete()
            return redirect('intent-list')
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, pk, format=None):
        print('request.data: ', request.data)
        intent = self.get_object(pk)
        serializer = IntentSerializer(instance=intent, data=request.data)

        if serializer.is_valid():
            serializer.save()

            id_kg = request.data['intent_texts[0][id]']
            id_ru = request.data['intent_texts[1][id]']

            texts_kg = request.data.getlist(f'intent_texts[0][texts][]')
            texts_data_raw_kg = [text.split(';') for text in texts_kg]
            texts_data_kg = texts_data_raw_kg[0]

            texts_ru = request.data.getlist(f'intent_texts[1][texts][]')
            texts_data_raw_ru = [text.split(';') for text in texts_ru]
            texts_data_ru = texts_data_raw_ru[0]

            intent_text_data_kg = {
                'id': id_kg,
                'language': request.data.get(f'intent_texts[0][language]'),
                'texts': texts_data_kg,
                'responses': request.data.getlist(f'intent_texts[0][responses][]'),
                'intent': pk,
            }
            intent_text_data_ru = {
                'id': id_ru,
                'language': request.data.get(f'intent_texts[1][language]'),
                'texts': texts_data_ru,
                'responses': request.data.getlist(f'intent_texts[1][responses][]'),
                'intent': pk,
            }

            intent_text_kg = intent.intent_texts.get(id=id_kg)
            intent_text_ru = intent.intent_texts.get(id=id_ru)

            intent_text_serializer_kg = IntentTextSerializer(instance=intent_text_kg, data=intent_text_data_kg)
            intent_text_serializer_ru = IntentTextSerializer(instance=intent_text_ru, data=intent_text_data_ru)

            if intent_text_serializer_kg.is_valid() and intent_text_serializer_ru.is_valid():
                intent_text_serializer_kg.save()
                intent_text_serializer_ru.save()
            else:
                return render(request, 'intent-detail.html', {'errors': intent_text_serializer_kg.errors}, {'errors': intent_text_serializer_ru.errors})

            return redirect('intent-detail', pk=pk)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)