document.addEventListener(
    "DOMContentLoaded",
    () => {

        const form =
            document.querySelector(
                "#plan-form"
            );


        if (form) {

            form.addEventListener(
                "submit",
                () => {

                    const button =
                        form.querySelector(
                            "button[type=submit]"
                        );


                    if (button) {

                        button.disabled = true;

                        button.textContent =
                            "Generating your plan...";
                    }
                }
            );
        }
    }
);