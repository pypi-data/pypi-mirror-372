odoo.define("ssi_mail_telegram.loader", function (require) {
    "use strict";

    var rpc = require("web.rpc");

    function loadTelegramLinks() {
        var placeholders = document.querySelectorAll(
            ".telegram-links-placeholder:not(.processed)"
        );
        if (placeholders.length === 0) return;

        var messageIds = [];
        placeholders.forEach(function (placeholder) {
            var messageId = parseInt(placeholder.getAttribute("data-message-id"));
            if (messageId) {
                messageIds.push(messageId);
                placeholder.classList.add("processed");
            }
        });

        if (messageIds.length === 0) return;

        rpc.query({
            model: "mail.message.telegram",
            method: "get_message_telegram_links",
            args: [messageIds],
        }).then(function (result) {
            placeholders.forEach(function (placeholder) {
                var messageId = parseInt(placeholder.getAttribute("data-message-id"));
                var links = result[messageId] || [];

                if (links.length > 0) {
                    var messageContainer =
                        placeholder.closest(".o_Message") ||
                        placeholder.closest(".o_mail_message");
                    var messageBody = messageContainer
                        ? messageContainer.querySelector(
                              ".o_Message_content, .o_mail_message_content"
                          )
                        : null;

                    var html =
                        '<div class="o_Message_telegram_links mt-2 p-2 border-top" style="background-color: #f8f9fa;">';
                    links.forEach(function (link) {
                        html += '<div class="mb-1">';
                        html += '<i class="fa fa-telegram text-primary mr-1"></i>';
                        html += '<small class="text-muted">Sent to Telegram: </small>';

                        if (link.can_link && link.url) {
                            html +=
                                '<a href="' +
                                link.url +
                                '" target="_blank" class="small text-primary" onclick="return confirmTelegramLink()">View in Telegram</a>';
                            html +=
                                ' <span class="small text-muted">(' +
                                (link.chat_description || link.chat_id) +
                                ")</span>";
                        } else {
                            html +=
                                '<span class="small text-info">' +
                                (link.chat_description || link.chat_id) +
                                "</span>";
                            html +=
                                ' <small class="text-muted">(Private group - cannot create direct link)</small>';
                        }
                        html += "</div>";
                    });
                    html += "</div>";

                    if (messageBody) {
                        messageBody.insertAdjacentHTML("afterend", html);
                        placeholder.style.display = "none";
                    } else {
                        placeholder.innerHTML = html;
                    }
                }
            });
        });
    }

    $(document).ready(function () {
        loadTelegramLinks();

        var observer = new MutationObserver(function (mutations) {
            var shouldLoad = false;
            mutations.forEach(function (mutation) {
                if (mutation.addedNodes) {
                    mutation.addedNodes.forEach(function (node) {
                        if (
                            node.nodeType === 1 &&
                            node.querySelector &&
                            node.querySelector(".telegram-links-placeholder")
                        ) {
                            shouldLoad = true;
                        }
                    });
                }
            });
            if (shouldLoad) {
                setTimeout(loadTelegramLinks, 100);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    });

    window.confirmTelegramLink = function () {
        return confirm(
            "You are about to open a Telegram link. Make sure you are a member of the group/channel."
        );
    };
});
