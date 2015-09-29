-- rule
INSERT INTO rule (title, description, created_at, updated_at)
VALUES (
  'Blog Kafka',
  'Regel zum Abrufen von Comments vom wunderschoenen Kafka Blog :)',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
);
-- create action for rule
INSERT INTO action (rule_id, position, method, url, parse_expression, parse_type)
VALUES (
  1,
  0,
  'GET',
  'http://www2.mi.hs-rm.de/~jthei001/wsgi/blatt2/aufg3/blog.wsgi/blog/Kafka',
  '//*[@id=''content'']/div/div/div/div[last()]',
  'XPATH'
);


-- rule QIS
INSERT INTO rule (title, description, created_at, updated_at)
VALUES (
  'QIS',
  'Programmieren 1 Gesamtnote mit Anzahl der CreditPoints von dem geliebten QIS.',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
);

-- create action for getting url to Login
INSERT INTO action (title, rule_id, position, method, url, parse_expression, parse_type)
VALUES (
  'Get Login URL',
  2,
  0,
  'GET',
  'https://qis.hs-rm.de/',
  '//*[@id="wrapper"]/div[6]/div[2]/div/div/form/@action',
  'XPATH'
);

-- create action to login
INSERT INTO action (title, rule_id, position, method, parse_expression, parse_type)
VALUES (
  'Login',
  2,
  1,
  'POST',
  '//*[@id="makronavigation"]/ul/li[2]/a/@href',
  'XPATH'
);
-- create action_params for action Login for rule QIS
INSERT INTO action_param (title, action_id, key, type)
VALUES (
  'Benutzerkennung',
  3,
  'asdf',
  'string'
);
-- create action_params for action Login for rule QIS
INSERT INTO action_param (title, action_id, key, type)
VALUES (
  'Passwort',
  3,
  'fdsa',
  'password'
);
-- create click to "Prüfungsverwaltung"
INSERT INTO action (title, rule_id, position, method, parse_expression, parse_type)
VALUES (
  'Prüfungsverwaltung',
  2,
  2,
  'GET',
  '//*[@id="wrapper"]/div[6]/div[2]/div/form/div/ul/li[4]/a/@href',
  'XPATH'
);
-- create click to "Notenspiegel"
INSERT INTO action (title, rule_id, position, method, parse_expression, parse_type)
VALUES (
  'Notenspiegel',
  2,
  3,
  'GET',
  '//*[@id="wrapper"]/div[6]/div[2]/form/ul[1]/li/a[1]/@href',
  'XPATH'
);
-- create click to "Abschluss Bachelor"
INSERT INTO action (title, rule_id, position, method, parse_expression, parse_type)
VALUES (
  'Abschluss Bachelor',
  2,
  4,
  'GET',
  '//*[@id="wrapper"]/div[6]/div[2]/form/ul[1]/li/ul/li/a[1]/@href',
  'XPATH'
);
-- create click to "info"
INSERT INTO action (title, rule_id, position, method, parse_expression, parse_type, parse_expression_display, parse_type_display)
VALUES (
  'Info Icon & Parsen',
  2,
  5,
  'GET',
  '//*[@id="wrapper"]/div[6]/div[2]/form/table[2]/tbody/tr[contains(., "1120")]/td[5]',
  'XPATH',
  '//*[@id="wrapper"]/div[6]/div[2]/form/table[2]/tbody/tr[contains(., "1120")]',
  'XPATH'
);



-- rule check price
INSERT INTO rule (title, description, created_at, updated_at)
VALUES (
  'Preisalarm Alabama Frankenstein',
  'Dellstore Preisalarm für Alabama Frankenstein',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
);
-- create login action for check price
INSERT INTO action (title, rule_id, position, method, url)
VALUES (
  'Login',
  3,
  0,
  'POST',
  'http://www2.mi.hs-rm.de/~tginz001/wsgi/abgabe1/user.wsgi'
);
-- create action_params for action Login for check price
INSERT INTO action_param (title, action_id, key, type)
VALUES (
  'Benutzername',
  8,
  'username',
  'string'
);
-- create action_params for action Login for check price
INSERT INTO action_param (title, action_id, key, type)
VALUES (
  'Passwort',
  8,
  'password',
  'password'
);
-- create action_params for action Login for check price
INSERT INTO action_param (action_id, key, value, type)
VALUES (
  8,
  'login',
  'Einloggen',
  'invisible'
);
-- create parse action for rule QIS
INSERT INTO action (title, rule_id, position, method, url, parse_expression, parse_type)
VALUES (
  'Content parsen',
  3,
  1,
  'GET',
  'http://www2.mi.hs-rm.de/~tginz001/wsgi/abgabe1/user.wsgi/products/8332/',
  '#content > div > div.col-md-10 > table > tbody > tr:nth-child(2) > td:nth-child(5)',
  'CSS'
);



-- rule
INSERT INTO rule (title, description, created_at, updated_at)
VALUES (
  'Produktfehler 404',
  'Signalisierung, dass eine Seite nicht gefunden wurde via 404.',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
);
-- create action for rule
INSERT INTO action (rule_id, position, method, url, parse_expression, parse_type)
VALUES (
  4,
  0,
  'GET',
  'http://www.mi.hs-rm.de/~tginz001/wsgi/abgabe1/employee.wsgi/customers/adjhad',
  'body .comment',
  'CSS'
);


-- rule
INSERT INTO rule (title, description, created_at, updated_at)
VALUES (
  'Fehler (kein Content)',
  'Hier kann kein Inhalt für den gewählten Parse-Ausruck gefunden werden.',
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
);
-- create action for rule
INSERT INTO action (rule_id, position, method, url, parse_expression, parse_type)
VALUES (
  5,
  0,
  'GET',
  'http://www.mi.hs-rm.de/~tginz001/wsgi/abgabe1/employee.wsgi/',
  'body .comment',
  'CSS'
);

