Changelog
=========


2.1.3 (2025-08-29)
------------------

- Fix deleting user with already loggued.
  [bsuttor]


2.1.2 (2025-08-29)
------------------

- Fix deleting user with "tab" in name.
  [bsuttor]


2.1.1 (2025-07-15)
------------------

- Add email to getUsers method to make migration to keycloak.
  [bsuttor]


2.1 (2025-04-25)
----------------

- Plone 6.1 compatibility.
  [remdub]


2.0.9 (2023-08-31)
------------------

- Fix login could be id of user.
  [bsuttor]

- Fix byte convertion error on python3.
  [bsuttor]


2.0.8 (2023-08-18)
------------------

- Fix bug in users enumeration: wrong user could be retrieved (#4)
  [laulaz]

- Finally check certs on JWT call (except for test).
  [bsuttor]

- Fix creation of user on JWT call and test it.
  [bsuttor]


2.0.7 (2023-03-28)
------------------

- Keep old groups during first login.
  [bsuttor]


2.0.6 (2022-07-18)
------------------

- Do not verify_signature for jwt call because of error: "Could not deserialize key data".
  [bsuttor]


2.0.5 (2022-07-13)
------------------

- Keep old roles on migration of users.
  [bsuttor]


2.0.4 (2022-07-13)
------------------

- Temporary remove pas.app.users override because it do not work on Plone 6.
  [bsuttor]

- Add possibility to remove old user (without login).
  [bsuttor]


2.0.3 (2022-06-29)
------------------

- Migration code refactoring & add tests
  [laulaz]


2.0.2 (2022-06-29)
------------------

- Add migration code (to new userid) for local roles / ownership
  [laulaz]


2.0.1 (2022-06-15)
------------------

- Add posibility to delete user on zmi view.
  [bsuttor]

- Improve user migration code
  [laulaz]

- Verify signature for login with JWT.
  [bsuttor]


2.0 (2022-06-01)
----------------

- Get userid and user login for user connected by JWT.
  [bsuttor]

- Allow user search on any parts of id/login/email (not just the start)
  [laulaz]

- Use uuid as plone user.id instead of username.
  [bsuttor, laulaz]

- Be aware of next url when you call auhentic users api.
  [bsuttor]

- Add zmi view of users.
  [bsuttor]


1.0.11 (2022-04-21)
-------------------

- Revert previous release.
  [bsuttor]


1.0.10 (2022-04-21)
-------------------

- Nothing changed yet.


1.0.9 (2022-01-19)
------------------

- Get rid of includeDependencies for Plone 6 compatibility.
  [laulaz]


1.0.8 (2021-10-15)
------------------

- Fill username when user is created with JWT.
  [bsuttor]


1.0.7 (2021-10-15)
------------------

- Create user with JWT token on first connection.
  [bsuttor]


1.0.6 (2021-06-01)
------------------

- Fixed ModuleNotFoundError: No module named 'App.class_init' on Zope 5.
  [bsuttor]

- Add JWT support.
  [bsuttor]


1.0.5 (2021-01-04)
------------------

- Improve Anysurfer integration.
  [bsuttor]

- Added revoke-user-access page to remove a user from its groups and revoke its roles.
  [odelaere]


1.0.4 (2020-10-08)
------------------

- Plugin also provide IUserIntrospection so user from Authentic PAS plugin will also listed in api.user.get_users().
  [bsuttor]

- Use IItem for Object to redirect imio_login instead of INavigation. It's solved bug to redirect from other page than root navigation, and so page which required access.
  [bsuttor]

- Fix redirect after login for Plone < 5.2.
  [odelaere]


1.0.3 (2020-07-30)
------------------

- Add Plone 5 testing profile.
  [bsuttor]


1.0.2 (2020-07-16)
------------------

- Fix(testing profile): dependency of plone4 profile do not exists, use default.
  [bsuttor]


1.0.1 (2020-07-16)
------------------

- Add plone 4 testing profile.
  [bsuttor]

- Do not install usager login by default.
  [bsuttor]

- Fix: import zcml permission from plone.app.controlpanel
  [bsuttor]


1.0.0 (2020-05-29)
------------------

- Fix: set username on python3 when new user added.
  [bsuttor]


1.0b11 (2020-03-27)
-------------------

- Also see came_from on request for next url.
  [bsuttor]


1.0b10 (2020-03-27)
-------------------

- Fix: redirect on homepage.
  [bsuttor]

- Improve next_url login.
  [bsuttor]


1.0b9 (2020-02-26)
------------------

- Use state / user_state to redirect to page which apply SSO.
  [bsuttor]


1.0b8 (2020-02-21)
------------------

- Set talk less.
  [bsuttor]


1.0b7 (2020-02-11)
------------------

- Fix french typo.
  [bsuttor]


1.0b6 (2020-02-07)
------------------

- Add plone.app.changeownership dependency.
  [bsuttor]


1.0b5 (2020-02-07)
------------------

- Improve python3 compatibility, check if python 2 before safe_utf8.
  [bsuttor]


1.0b4 (2020-02-07)
------------------

- Bad release.
  [bsuttor]


1.0b3 (2020-02-07)
------------------

- Override plone userlist page to add link to WCA on Plone 5.
  [bsuttor]

- Add zope_login to bypass SSO auth.
  [bsuttor]


1.0b2 (2020-02-04)
------------------

- Fix python3 EnumerateUsers.
  [bsuttor]

- Override plone userlist page to add link to WCA.
  [bsuttor]


1.0b1 (2019-12-16)
------------------

- Python 3 support.
  [bsuttor]


1.0a10 (2019-11-18)
-------------------

- Add css for login-page
  [bsuttor]

- Add fr translations.
  [bsuttor]


1.0a9 (2019-11-05)
------------------

- Override default login_form template (with z3c.jbot) to allow login with zope admin and an external url set.
  [bsuttor]


1.0a8 (2019-09-04)
------------------

- Set Site Manager role to user with admin of service role on Authentic.
  [bsuttor]


1.0a7 (2019-06-28)
------------------

- Set Manager role if you are into admin role on Authentic.
  [bsuttor]

- Add Member role to user connected with Authentic.
  [bsuttor]


1.0a6 (2019-05-20)
------------------

- Get logout hostname redirect from agents config.
  [bsuttor]

- Add roles scope on agents.
  [bsuttor]


1.0a5 (2019-05-09)
------------------

- Add userfactories to connect with email for usagers and with userid of agents.
  [bsuttor]


1.0a4 (2019-04-26)
------------------

- Use different OU for usagers and agents.
  [bsuttor]


1.0a3 (2019-04-25)
------------------

- Use different usagers and agents environement variables to connect to SOO.
  [bsuttor]


1.0a2 (2019-04-25)
------------------

- Use agents and usagers to connect to Plone.
  [bsuttor]


1.0a1 (2018-03-28)
------------------

- Initial release.
  [bsuttor]
