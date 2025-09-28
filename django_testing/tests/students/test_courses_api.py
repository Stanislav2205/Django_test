import pytest
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Course


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make('students.Student', *args, **kwargs)
    return factory


@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory):
    """Проверка получения первого курса"""
    course = course_factory(name="Python Basics")
    url = f"/api/v1/courses/{course.id}/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == course.id
    assert response.data['name'] == course.name


@pytest.mark.django_db
def test_list_courses(api_client, course_factory):
    """Проверка получения списка курсов"""
    courses = course_factory(_quantity=3)
    url = "/api/v1/courses/"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == len(courses)

    response_ids = {item['id'] for item in response.data}
    created_ids = {course.id for course in courses}
    assert response_ids == created_ids


@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):
    """Проверка фильтрации курсов по id"""

    course1 = course_factory(name="Course 1")
    course2 = course_factory(name="Course 2")

    url = "/api/v1/courses/"
    response = api_client.get(url, data={'id': course1.id})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == course1.id


@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):
    """Проверка фильтрации списка курсов по названию"""
    course1 = course_factory(name="Django Course")
    course2 = course_factory(name="Flask Course")

    url = "/api/v1/courses/"
    response = api_client.get(url, data={'name': 'Django'})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['name'] == "Django Course"


@pytest.mark.django_db
def test_create_course_success(api_client):
    """Тест успешного создания курса"""
    data = {
        "name": "New Test Course",
        "students": []
    }

    url = "/api/v1/courses/"
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == "New Test Course"
    assert Course.objects.filter(name="New Test Course").exists()


@pytest.mark.django_db
def test_update_course_success(api_client, course_factory):
    """Тест успешного обновления курса"""
    course = course_factory(name="Old Name")

    data = {
        "name": "Updated Name",
        "students": []
    }

    url = f"/api/v1/courses/{course.id}/"
    response = api_client.put(url, data=data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == "Updated Name"
    course.refresh_from_db()
    assert course.name == "Updated Name"


@pytest.mark.django_db
def test_delete_course_success(api_client, course_factory):
    """Тест успешного удаления курса"""
    course = course_factory(name="To Be Deleted")

    url = f"/api/v1/courses/{course.id}/"
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Course.objects.filter(id=course.id).exists()