/**
 * Created by zjianglin on 2017/4/17.
 */

$(document).ready(function() {
    $('#build_model_form').bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        },
        fields: {
            target: {
                validators: {
                    notEmpty: { message: 'target is required'},

                }
            }
        }
    })
})