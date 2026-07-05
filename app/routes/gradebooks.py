from flask import Blueprint, request
from app.routes.oauth import GRADEBOOK_READONLY_SCOPE, GRADEBOOK_CREATEPUT_SCOPE, GRADEBOOK_DELETE_SCOPE, bearer_token_required
from app.models.Category import Category
from app.models.LineItem import LineItem
from app.models.Result import Result
from .. import db
gradebooks = Blueprint('gradebooks', __name__)
from app.utils.collection_response import collection_response


@gradebooks.route('/categories', methods=['GET'])
@bearer_token_required(GRADEBOOK_READONLY_SCOPE)
def getAllCategories() -> dict:
    categories = Category.query.all()
    return collection_response("categories", [cat.to_dict() for cat in categories])

@gradebooks.route('/categories/<id>', methods=['GET'])
@bearer_token_required(GRADEBOOK_READONLY_SCOPE)
def getCategory(id) -> dict:
    category = Category.get_by_sourced_id(id)
    if not category:
        return {"error": "Not found"}, 404
    return {"category": category.to_dict()}

@gradebooks.route('/categories/<id>', methods=['DELETE'])
@bearer_token_required(GRADEBOOK_DELETE_SCOPE)
def deleteCategory(id) -> dict:
    category = Category.get_by_sourced_id(id)
    if not category:
        return {"error": "Not found"}, 404
    db.session.delete(category)
    db.session.commit()
    return {"message": "Deleted"}, 204

@gradebooks.route('/categories/<id>', methods=['PUT'])
@bearer_token_required(GRADEBOOK_CREATEPUT_SCOPE)
def putCategory(id) -> dict:
    request_data = request.get_json()
    category = Category.get_by_sourced_id(id)
    if not category:
        return {"error": "Not found"}, 404
    for key, value in request_data.items():
        setattr(category, key, value)
    db.session.commit()
    return {"category": category.to_dict()}

@gradebooks.route('/lineItems', methods=['GET'])
@bearer_token_required(GRADEBOOK_READONLY_SCOPE)
def getAllLineItems() -> dict:
    line_items = LineItem.query.all()
    return collection_response("lineItems", [li.to_dict() for li in line_items])

@gradebooks.route('/lineItems/<id>', methods=['GET'])
@bearer_token_required(GRADEBOOK_READONLY_SCOPE)
def getLineItem(id) -> dict:
    line_item = LineItem.get_by_sourced_id(id)
    if not line_item:
        return {"error": "Not found"}, 404
    return {"lineItem": line_item.to_dict()}

@gradebooks.route('/lineItems/<id>', methods=['DELETE'])
@bearer_token_required(GRADEBOOK_DELETE_SCOPE)
def deleteLineItem(id) -> dict:
    line_item = LineItem.get_by_sourced_id(id)
    if not line_item:
        return {"error": "Not found"}, 404
    db.session.delete(line_item)
    db.session.commit()
    return {"message": "Deleted"}, 204

@gradebooks.route('/lineItems/<id>', methods=['PUT'])
@bearer_token_required(GRADEBOOK_CREATEPUT_SCOPE)
def putLineItem(id) -> dict:
    request_data = request.get_json()
    line_item = LineItem.get_by_sourced_id(id)
    if not line_item:
        return {"error": "Not found"}, 404
    for key, value in request_data.items():
        setattr(line_item, key, value)
    db.session.commit()
    return {"lineItem": line_item.to_dict()}

@gradebooks.route('/results', methods=['GET'])
@bearer_token_required(GRADEBOOK_READONLY_SCOPE)
def getAllResults() -> dict:
    results = Result.query.all()
    return collection_response("results", [res.to_dict() for res in results])

@gradebooks.route('/results/<id>', methods=['GET'])
@bearer_token_required(GRADEBOOK_READONLY_SCOPE)
def getResult(id) -> dict:
    result = Result.get_by_sourced_id(id)
    if not result:
        return {"error": "Not found"}, 404
    return {"result": result.to_dict()}

@gradebooks.route('/results/<id>', methods=['DELETE'])
@bearer_token_required(GRADEBOOK_DELETE_SCOPE)
def deleteResult(id) -> dict:
    result = Result.get_by_sourced_id(id)
    if not result:
        return {"error": "Not found"}, 404
    db.session.delete(result)
    db.session.commit()
    return {"message": "Deleted"}, 204

@gradebooks.route('/results/<id>', methods=['PUT'])
@bearer_token_required(GRADEBOOK_CREATEPUT_SCOPE)
def putResult(id) -> dict:
    request_data = request.get_json()
    result = Result.get_by_sourced_id(id)
    if not result:
        return {"error": "Not found"}, 404
    for key, value in request_data.items():
        setattr(result, key, value)
    db.session.commit()
    return {"result": result.to_dict()}

@gradebooks.route('/classes/<class_id>/results', methods=['GET'])
@bearer_token_required(GRADEBOOK_READONLY_SCOPE)
def getResultsForClass(class_id) -> dict:
    line_item_ids = [
        line_item.sourcedId
        for line_item in LineItem.query.filter_by(classSourcedId=class_id).all()
    ]
    results = Result.query.filter(Result.lineItemSourcedId.in_(line_item_ids)).all()
    return collection_response("results", [res.to_dict() for res in results])

@gradebooks.route('/classes/<class_id>/lineItems', methods=['GET'])
@bearer_token_required(GRADEBOOK_READONLY_SCOPE)
def getLineItemsForClass(class_id) -> dict:
    line_items = LineItem.query.filter_by(classSourcedId=class_id).all()
    return collection_response("lineItems", [li.to_dict() for li in line_items])

@gradebooks.route('/classes/<class_id>/lineItems/<li_id>/results', methods=['GET'])
@bearer_token_required(GRADEBOOK_READONLY_SCOPE)
def getResultsForLineItemForClass(class_id, li_id) -> dict:
    line_item = LineItem.query.filter_by(sourcedId=li_id, classSourcedId=class_id).first()
    if not line_item:
        return {"error": "Not found"}, 404
    results = Result.query.filter_by(lineItemSourcedId=li_id).all()
    return collection_response("results", [res.to_dict() for res in results])

@gradebooks.route('/classes/<class_id>/students/<student_id>/results', methods=['GET'])
@bearer_token_required(GRADEBOOK_READONLY_SCOPE)
def getResultsForStudentForClass(class_id, student_id) -> dict:
    line_item_ids = [
        line_item.sourcedId
        for line_item in LineItem.query.filter_by(classSourcedId=class_id).all()
    ]
    results = Result.query.filter(
        Result.lineItemSourcedId.in_(line_item_ids),
        Result.studentSourcedId == student_id,
    ).all()
    return collection_response("results", [res.to_dict() for res in results])
