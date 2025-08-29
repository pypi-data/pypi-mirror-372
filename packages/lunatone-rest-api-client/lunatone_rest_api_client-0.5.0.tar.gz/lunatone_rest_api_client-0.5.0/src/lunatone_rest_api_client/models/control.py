from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, NonNegativeFloat, NonNegativeInt

from lunatone_rest_api_client.models.common import (
    ColorRGBData,
    ColorWAFData,
    ColorWithFadeTime,
    ColorXYData,
    DimmableKelvinData,
    DimmableRGBData,
    DimmableWAFData,
    DimmableWithFadeTime,
    DimmableXYData,
    FadeTime,
)


class SceneWithFadeData(FadeTime):
    scene: int = Field(ge=0, lt=16)


class ControlData(BaseModel):
    """Data model for ``ControlData``."""

    switchable: Optional[bool] = None
    dimmable: Optional[float] = Field(None, ge=0.0, le=100.0)
    dimmable_with_fade: Optional[DimmableWithFadeTime] = Field(
        None, alias="dimmableWithFade"
    )
    dim_up: Optional[int] = Field(None, alias="dimUp", ge=1, le=1)
    dim_down: Optional[int] = Field(None, alias="dimDown", ge=1, le=1)
    goto_last_active: Optional[bool] = Field(
        None,
        description="Value must be ``true``.",
        alias="gotoLastActive",
    )
    goto_last_active_with_fade: Optional[FadeTime] = Field(
        None,
        description="Dim to the last level within a fade time in seconds.",
        alias="gotoLastActiveWithFade",
    )
    scene: Optional[int] = Field(
        None,
        description="Scene number of the scene to recall.",
        ge=0,
        lt=16,
    )
    scene_with_fade: Optional[SceneWithFadeData] = Field(
        None,
        description="Scene number of the scene to recall, within a fade time in seconds.",
        alias="sceneWithFade",
    )
    fade_time: Optional[NonNegativeFloat] = Field(
        None,
        description="Set the fade time in seconds.",
        alias="fadeTime",
    )
    fade_rate: Optional[NonNegativeFloat] = Field(
        None,
        description="Set the fade rate in steps per second.",
        alias="fadeRate",
    )
    save_to_scene: Optional[NonNegativeInt] = Field(
        None, alias="saveToScene", ge=0, lt=16
    )
    color_rgb: Optional[ColorRGBData] = Field(None, alias="colorRGB")
    dimmable_rgb: Optional[DimmableRGBData] = Field(None, alias="dimmableRGB")
    color_rgb_with_fade: Optional[ColorWithFadeTime[ColorRGBData]] = Field(
        None, alias="colorRGBWithFade"
    )
    color_waf: Optional[ColorWAFData] = Field(None, alias="colorWAF")
    dimmable_waf: Optional[DimmableWAFData] = Field(None, alias="dimmableWAF")
    color_waf_with_fade: Optional[ColorWithFadeTime[ColorWAFData]] = Field(
        None, alias="colorWAFWithFade"
    )
    color_kelvin: Optional[NonNegativeInt] = Field(
        None, alias="colorKelvin", gt=15, le=1000000
    )
    dimmable_kelvin: Optional[DimmableKelvinData] = Field(None, alias="dimmableKelvin")
    color_kelvin_with_fade: Optional[ColorWithFadeTime[NonNegativeFloat]] = Field(
        None, alias="colorKelvinWithFade"
    )
    color_xy: Optional[ColorXYData] = Field(None, alias="colorXY")
    dimmable_xy: Optional[DimmableXYData] = Field(None, alias="dimmableXY")
    color_xy_with_fade: Optional[ColorWithFadeTime[ColorXYData]] = Field(
        None, alias="colorXYWithFade"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "gotoLastActive": True,
                    "gotoLastActiveWithFade": FadeTime(fadeTime=1.0),
                    "scene": 15,
                    "sceneWithFade": SceneWithFadeData(scene=15, fadeTime=1.0),
                    "fadeTime": 1.0,
                    "fadeRate": 15.8,
                }
            ]
        }
    )
