const file_html_data =  "<div class=\"mdc-card\"\n" +
                        "     style=\"cursor: pointer;background-color: #333333\">\n" +
                        "    <img class=\"mdc-card__media mdc-card__media--16-9\" src=\"/getAssets?res=mime-type-icon/{1}&path={2}\" style=\"width: 100%;\" alt=\"cover\"/>\n" +
                        "    <ul class=\"mdc-list\">\n" +
                        "        <li class=\"{6} mdc-list-item file-dialog-name__text demo-card__title\" style=\"padding-left: 20px;width: auto;align-items: baseline;\">\n" +
                        "            {0}\n" +
                        "        </li>\n" +
                        "    </ul>\n" +
                        "    <div class=\"mdc-card__actions mdc-dialog__actions_\">\n" +
                        "        <div class=\"mdc-dialog__actions\">\n" +
                        "            <button type=\"button\" class=\"material-icons mdc-icon-button mdc-dialog__button mdc-card__action--icon\"\n" +
                        "                    onclick=\"onDialogButtonClick('{3}','play')\">\n" +
                        "                play_circle\n" +
                        "            </button>\n" +
                        "        </div>\n" +
                        "        <div class=\"mdc-card__action-icons\">\n" +
                        "            <button class=\"material-icons mdc-icon-button mdc-card__action mdc-card__action--icon dialog-copy\"\n" +
                        "                    data-mdc-dialog-action=\"1\" title=\"copy link\"\n" +
                        "                    onclick=\"onDialogButtonClick('{3}','copy')\">link\n" +
                        "            </button>\n" +
                        "            <button class=\"material-icons mdc-icon-button mdc-card__action mdc-card__action--icon\"\n" +
                        "                    data-mdc-dialog-action=\"2\" title=\"download\"\n" +
                        "                    onclick=\"onDialogButtonClick('{3}','download')\">\n" +
                        "                download\n" +
                        "            </button>\n" +
                        "            <button class=\"material-icons mdc-icon-button mdc-card__action mdc-card__action--icon\"\n" +
                        "                    data-mdc-dialog-action=\"3\" title=\"add/remove bookmark\"\n" +
                        "                    onclick=\"onDialogButtonClick('{4}','bookmark')\">{5}\n" +
                        "            </button>\n" +
                        "        </div>\n" +
                        "    </div>\n" +
                        "</div>";
const directory_html_data = "<div class=\"mdc-card\" style=\"height: fit-content;cursor: pointer;background-color: #333333\" onclick=\"onItemClick('{0}','Directory','')\">\n" +
                            "    <img class=\"mdc-card__media\" src=\"/getCover?cover={0}\" style=\"width: 100%;\" alt=\"{0}\"/>\n" +
                            "    <span class=\"ipc-rating-star ipc-rating-star--baseAlt ipc-rating-star--imdb\" style=\"padding: 10px 5px;\"></span>\n" +
                            "    <div class=\"mdc-card-wrapper__text-section\">\n" +
                            "        <div class=\"demo-card__title\">{1}</div>\n" +
                            "    </div>\n" +
                            "</div>";
