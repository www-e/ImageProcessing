"""
History management routes for the Image Processing application
"""
from flask import Blueprint, request, jsonify
from services.history_manager import HistoryManager

# Create a blueprint for history routes
history_bp = Blueprint('history', __name__)

# Create a history manager instance
history_manager = HistoryManager()

@history_bp.route('/history', methods=['GET'])
def get_history():
    """Get all history entries"""
    try:
        history = history_manager.get_history()
        return jsonify(success=True, history=history)
    except Exception as e:
        print(f"Error getting history: {str(e)}")
        return jsonify(success=False, error=f'Error getting history: {str(e)}')

@history_bp.route('/history/<entry_id>', methods=['GET'])
def get_history_entry(entry_id):
    """Get a specific history entry"""
    try:
        entry = history_manager.get_entry(entry_id)
        if not entry:
            return jsonify(success=False, error='History entry not found')
        return jsonify(success=True, entry=entry)
    except Exception as e:
        print(f"Error getting history entry: {str(e)}")
        return jsonify(success=False, error=f'Error getting history entry: {str(e)}')

@history_bp.route('/history/<entry_id>', methods=['DELETE'])
def delete_history_entry(entry_id):
    """Delete a specific history entry"""
    try:
        success = history_manager.delete_entry(entry_id)
        if not success:
            return jsonify(success=False, error='History entry not found')
        return jsonify(success=True)
    except Exception as e:
        print(f"Error deleting history entry: {str(e)}")
        return jsonify(success=False, error=f'Error deleting history entry: {str(e)}')

@history_bp.route('/history', methods=['DELETE'])
def clear_history():
    """Clear all history entries"""
    try:
        count = history_manager.clear_history()
        return jsonify(success=True, count=count)
    except Exception as e:
        print(f"Error clearing history: {str(e)}")
        return jsonify(success=False, error=f'Error clearing history: {str(e)}')
