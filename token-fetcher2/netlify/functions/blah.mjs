const express = require("express");
const axios = require("axios");
const { formatISO } = require("date-fns");

const app = express();
const PORT = 3002;

const BEARER_TOKEN =
  "Bearer AAAAAAAAAAAAAAAAAAAAAFXzAwAAAAAAMHCxpeSDG1gLNLghVe8d74hl6k4%3DRUMF4xAQLsbeBhTSRrCiQpJtxoGWeyHrDb5te2jpGskWDFW82F";
const BASIC_HEADERS = {
  Authorization: BEARER_TOKEN,
  "Content-Type": "application/json",
  "User-Agent":
    "TwitterAndroid/9.95.0-release.0 (29950000-r-0) ONEPLUS+A3010/9 (OnePlus;ONEPLUS+A3010;OnePlus;OnePlus3;0;;1;2016)",
  "X-Twitter-API-Version": "5",
  "X-Twitter-Client": "TwitterAndroid",
  "X-Twitter-Client-Version": "9.95.0-release.0",
  "OS-Version": "28",
  "System-User-Agent":
    "Dalvik/2.1.0 (Linux; U; Android 9; ONEPLUS A3010 Build/PKQ1.181203.001)",
  "X-Twitter-Active-User": "yes",
};
const SUBTASK_VERSIONS = {
  generic_urt: 3,
  standard: 1,
  open_home_timeline: 1,
  app_locale_update: 1,
  enter_date: 1,
  email_verification: 3,
  enter_password: 5,
  enter_text: 5,
  one_tap: 2,
  cta: 7,
  single_sign_on: 1,
  fetch_persisted_data: 1,
  enter_username: 3,
  web_modal: 2,
  fetch_temporary_password: 1,
  menu_dialog: 1,
  sign_up_review: 5,
  interest_picker: 4,
  user_recommendations_urt: 3,
  in_app_notification: 1,
  sign_up: 2,
  typeahead_search: 1,
  user_recommendations_list: 4,
  cta_inline: 1,
  contacts_live_sync_permission_prompt: 3,
  choice_selection: 5,
  js_instrumentation: 1,
  alert_dialog_suppress_client_events: 1,
  privacy_options: 1,
  topics_selector: 1,
  wait_spinner: 3,
  tweet_selection_urt: 1,
  end_flow: 1,
  settings_list: 7,
  open_external_link: 1,
  phone_verification: 5,
  security_key: 3,
  select_banner: 2,
  upload_media: 1,
  web: 2,
  alert_dialog: 1,
  open_account: 2,
  action_list: 2,
  enter_phone: 2,
  open_link: 1,
  show_code: 1,
  update_users: 1,
  check_logged_in_account: 1,
  enter_email: 2,
  select_avatar: 4,
  location_permission_prompt: 2,
  notifications_permission_prompt: 4,
};

async function makeRequest() {
  try {
    const guestResponse = await axios.post(
      "https://api.twitter.com/1.1/guest/activate.json",
      null,
      { headers: { Authorization: BEARER_TOKEN } }
    );
    const guestToken = guestResponse.data.guest_token;

    const flowResponse = await axios.post(
      "https://api.twitter.com/1.1/onboarding/task.json?flow_name=welcome&api_version=1&known_device_token=&sim_country_code=us",
      {
        flow_token: null,
        input_flow_data: {
          country_code: null,
          flow_context: {
            start_location: { location: "splash_screen" },
          },
          requested_variant: null,
          target_user_id: 0,
        },
        subtask_versions: SUBTASK_VERSIONS,
      },
      { headers: { ...BASIC_HEADERS, "X-Guest-Token": guestToken } }
    );
    const flowToken = flowResponse.data.flow_token;

    const response = await axios.post(
      "https://api.twitter.com/1.1/onboarding/task.json",
      {
        flow_token: flowToken,
        subtask_inputs: [
          { open_link: { link: "next_link" }, subtask_id: "NextTaskOpenLink" },
        ],
        subtask_versions: SUBTASK_VERSIONS,
      },
      { headers: { ...BASIC_HEADERS, "X-Guest-Token": guestToken } }
    );

    return response.data;
  } catch (error) {
    console.error(error);
    throw error;
  }
}

exports.handler = async (event, context) => {
  try {
    const accountData = await makeRequest();
    const newAccount = accountData.subtasks?.find(
      (task) => task.open_account
    )?.open_account;

    if (newAccount) {
      newAccount.creation_time = formatISO(new Date());
      return {
        statusCode: 200,
        body: JSON.stringify(newAccount),
      };
    } else {
      return { statusCode: 404, body: "No new account generated" };
    }
  } catch (error) {
    return {
      statusCode: 500,
      body: "Error in generating account: " + error.message,
    };
  }
};
