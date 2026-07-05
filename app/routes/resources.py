from flask import Blueprint
from flask import current_app as app
from app.routes.oauth import RESOURCE_READONLY_SCOPE, bearer_token_required
from app.models.Class import Class
from app.models.Course import Course
from app.models.Resource import Resource
resources = Blueprint('resources', __name__)

from app.utils.collection_response import collection_response


@resources.route('/resources', methods=['GET'])
@bearer_token_required(RESOURCE_READONLY_SCOPE)
def getAllResources() -> dict:
    resources = Resource.query.all()
    return collection_response("resources", [res.to_dict() for res in resources])

@resources.route('/resources/<id>', methods=['GET'])
@bearer_token_required(RESOURCE_READONLY_SCOPE)
def getResource(id) -> dict:
    resource = Resource.get_by_sourced_id(id)
    if not resource:
        return {"error": "Not found"}, 404
    return {"resource": resource.to_dict()}

@resources.route('/courses/<course_id>/resources', methods=['GET'])
@bearer_token_required(RESOURCE_READONLY_SCOPE)
def getResourcesForCourse(course_id) -> dict:
    course = Course.get_by_sourced_id(course_id)
    if not course:
        return {"error": "Not found"}, 404
    resource_ids = course.resourceSourcedIds or []
    resources = Resource.query.filter(Resource.sourcedId.in_(resource_ids)).all()
    return collection_response("resources", [res.to_dict() for res in resources])

@resources.route('/classes/<class_id>/resources', methods=['GET'])
@bearer_token_required(RESOURCE_READONLY_SCOPE)
def getResourcesForClass(class_id) -> dict:
    cls = Class.get_by_sourced_id(class_id)
    if not cls:
        return {"error": "Not found"}, 404
    resource_ids = cls.resourceSourcedIds or []
    resources = Resource.query.filter(Resource.sourcedId.in_(resource_ids)).all()
    return collection_response("resources", [res.to_dict() for res in resources])
