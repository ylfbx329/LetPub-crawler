from flask import Blueprint, current_app, render_template

detail_bp = Blueprint('detail', __name__, url_prefix='/detail')


@detail_bp.route('/journal/<int:jid>')
def journal_detail(jid):
    df = current_app.config['data']
    journal = df[df['id'] == jid].to_dict(orient='records')[0]

    radar_data = {
        "name": journal["name"],
        "scores": {
            "声誉分": float(journal["reputation_score"] or 0),
            "影响力分": float(journal["influence_score"] or 0),
            "速度分": float(journal["speed_score"] or 0),
        }
    }

    letpub_rating = {
        "score": float(journal["letpub_score"] or 0),
        "people": int(journal["score_people"] or 0)
    }

    return render_template(
        "detail.html",
        journal=journal,
        radar_data=radar_data,
        letpub_rating=letpub_rating
    )
