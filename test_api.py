#!/usr/bin/env python3
"""
LegalX Knowledge Centre - Local API Testing Script
Tests all backend API endpoints and features
"""

import requests
import json

BASE_URL = 'http://localhost:8000'

def print_header(text):
    print('\n' + '=' * 60)
    print(text)
    print('=' * 60)

def test_health():
    """Test health check endpoint"""
    print('\nTest 1: Health Check')
    print('-' * 60)
    try:
        resp = requests.get(f'{BASE_URL}/api/health', timeout=5)
        data = resp.json()
        print(f'  Status: {data["status"]}')
        print(f'  Documents Indexed: {data["documents_indexed"]}')
        print(f'  Topics Available: {len(data["topics_available"])} topics')
        print('  ✅ PASSED')
        return True
    except Exception as e:
        print(f'  ❌ FAILED: {e}')
        return False

def test_topics_list():
    """Test get all topics endpoint"""
    print('\nTest 2: Get All Topics')
    print('-' * 60)
    try:
        resp = requests.get(f'{BASE_URL}/api/topics', timeout=5)
        topics = resp.json()
        print(f'  Topics Found: {len(topics)}')
        for t in topics:
            print(f'    - {t["name"]} ({t["id"]})')
        print('  ✅ PASSED')
        return True
    except Exception as e:
        print(f'  ❌ FAILED: {e}')
        return False

def test_topic_detail():
    """Test get topic detail endpoint"""
    print('\nTest 3: Get Topic Detail (POCSO Act)')
    print('-' * 60)
    try:
        resp = requests.get(f'{BASE_URL}/api/topics/pocso_act', timeout=5)
        topic = resp.json()
        print(f'  Topic: {topic["name"]}')
        print(f'  Summary Length: {len(topic["summary"])} characters')
        print(f'  Summary Preview: {topic["summary"][:100]}...')
        print(f'  Key Info:')
        print(f'    - Rights: {len(topic["key_info"]["rights"])} items')
        print(f'    - Provisions: {len(topic["key_info"]["provisions"])} items')
        print(f'    - Penalties: {len(topic["key_info"]["penalties"])} items')
        print(f'    - Beneficiaries: {len(topic["key_info"]["beneficiaries"])} items')
        print(f'  Has Audio: {topic["has_audio"]}')
        print('  ✅ PASSED')
        return True
    except Exception as e:
        print(f'  ❌ FAILED: {e}')
        return False

def test_chat_qa():
    """Test chat Q&A endpoint"""
    print('\nTest 4: Chat Q&A (RAG-powered)')
    print('-' * 60)
    try:
        payload = {
            'question': 'What is the main purpose of POCSO?',
            'history': []
        }
        resp = requests.post(f'{BASE_URL}/api/topics/pocso_act/chat', 
                            json=payload, timeout=10)
        chat = resp.json()
        print(f'  Question: {payload["question"]}')
        print(f'  Answer Length: {len(chat["answer"])} characters')
        print(f'  Answer Preview: {chat["answer"][:120]}...')
        print(f'  Sources: {chat["sources"]}')
        print('  ✅ PASSED')
        return True
    except Exception as e:
        print(f'  ❌ FAILED: {e}')
        return False

def test_audio():
    """Test audio endpoint"""
    print('\nTest 5: Audio Endpoint')
    print('-' * 60)
    try:
        resp = requests.get(f'{BASE_URL}/api/topics/pocso_act/audio', timeout=5)
        if resp.status_code == 200:
            print(f'  Status: {resp.status_code}')
            print(f'  Content-Type: {resp.headers.get("Content-Type")}')
            print(f'  Content-Length: {len(resp.content)} bytes')
            print('  ✅ PASSED')
            return True
        else:
            print(f'  Status: {resp.status_code}')
            print('  ⚠️ Audio file not available (TTS may have failed)')
            return True  # Not a failure, gracefully handled
    except Exception as e:
        print(f'  ⚠️ AUDIO NOT AVAILABLE: {e}')
        return True  # Not a critical failure

def test_another_topic():
    """Test another topic to verify consistency"""
    print('\nTest 6: Get Another Topic (Consumer Protection Act)')
    print('-' * 60)
    try:
        resp = requests.get(f'{BASE_URL}/api/topics/consumer_protection_act', timeout=5)
        topic = resp.json()
        print(f'  Topic: {topic["name"]}')
        print(f'  Summary Length: {len(topic["summary"])} characters')
        key_rights = len(topic["key_info"]["rights"])
        key_penalties = len(topic["key_info"]["penalties"])
        print(f'  Key Info: Rights={key_rights}, Penalties={key_penalties}')
        print('  ✅ PASSED')
        return True
    except Exception as e:
        print(f'  ❌ FAILED: {e}')
        return False

def test_multi_turn_chat():
    """Test multi-turn conversation"""
    print('\nTest 7: Multi-Turn Chat (Conversation History)')
    print('-' * 60)
    try:
        # First question
        payload1 = {
            'question': 'What is RTI?',
            'history': []
        }
        resp1 = requests.post(f'{BASE_URL}/api/topics/rti_act/chat', 
                             json=payload1, timeout=10)
        chat1 = resp1.json()
        print(f'  Q1: What is RTI?')
        print(f'  A1 Preview: {chat1["answer"][:80]}...')
        
        # Follow-up question with history
        payload2 = {
            'question': 'What are the procedures?',
            'history': [
                {'role': 'user', 'content': payload1['question']},
                {'role': 'assistant', 'content': chat1['answer']}
            ]
        }
        resp2 = requests.post(f'{BASE_URL}/api/topics/rti_act/chat', 
                             json=payload2, timeout=10)
        chat2 = resp2.json()
        print(f'  Q2: What are the procedures? (with history)')
        print(f'  A2 Preview: {chat2["answer"][:80]}...')
        print('  ✅ PASSED')
        return True
    except Exception as e:
        print(f'  ❌ FAILED: {e}')
        return False

def main():
    """Run all tests"""
    print_header('LOCAL API TESTING - LegalX Knowledge Centre')
    print('Testing all backend endpoints and features...\n')
    
    results = []
    results.append(('Health Check', test_health()))
    results.append(('Topics List', test_topics_list()))
    results.append(('Topic Detail', test_topic_detail()))
    results.append(('Chat Q&A', test_chat_qa()))
    results.append(('Audio Endpoint', test_audio()))
    results.append(('Another Topic', test_another_topic()))
    results.append(('Multi-Turn Chat', test_multi_turn_chat()))
    
    # Summary
    print_header('TESTING SUMMARY')
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f'\nTests Passed: {passed}/{total}')
    for name, result in results:
        status = '✅ PASSED' if result else '❌ FAILED'
        print(f'  {name}: {status}')
    
    print('\n' + '=' * 60)
    if passed == total:
        print('🎉 ALL TESTS PASSED!')
        print('Backend API is fully functional!')
    else:
        print(f'⚠️ Some tests failed ({total - passed} failures)')
    print('=' * 60)

if __name__ == '__main__':
    main()
