from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from fastpluggy.core.config import FastPluggyConfig
from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_view_builder, get_fastpluggy
from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.repository.app_settings import update_db_settings
from fastpluggy.core.widgets import FormWidget

app_settings_router = APIRouter(
    tags=["admin"],
)


@app_settings_router.api_route("/settings", methods=["GET", "POST"], name="app_settings")
async def app_settings(request: Request, db: Session = Depends(get_db),
                       view_builder=Depends(get_view_builder),
                       fast_pluggy = Depends(get_fastpluggy)):
    form_view = FormWidget(
        title="Application Settings",
        model=FastPluggyConfig,
        data=fast_pluggy.settings,
        submit_label="Save Settings",
    )
    # TODO: show if an authentication method is setup
    items = [
        form_view,
    ]
    if request.method == "POST":
        form_data = await request.form()

        form = form_view.get_form(form_data)
        if form.validate():
            new_params = dict(form_data)

            update_db_settings(current_settings=fast_pluggy.settings, db=db, new_params=new_params)

            fast_pluggy.load_app()

            FlashMessage.add(request, "Settings saved successfully!", "success")

    return view_builder.generate(
        request,
        title='Application Settings',
        widgets=items
    )
