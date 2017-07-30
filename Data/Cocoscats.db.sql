BEGIN TRANSACTION;
CREATE TABLE "Translator" (
  "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
  "ProjectID" TEXT NOT NULL REFERENCES "Project" ("ID"),
  "Content" TEXT NOT NULL,
  "ContentParsed" JSON NOT NULL,
  "PluginName" TEXT NOT NULL,
  "PluginMethod" TEXT NOT NULL,
  "Plugin" JSON
);
CREATE TABLE "Project" (
  "ID" TEXT NOT NULL PRIMARY KEY,
  "Title" TEXT NOT NULL,
  "Description" TEXT NOT NULL,
  "DateTime" TEXT NOT NULL,
  "Workflow" JSON
);
CREATE TABLE "Output" (
  "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
  "ProjectID" TEXT NOT NULL REFERENCES "Project" ("ID"),
  "Content" TEXT NOT NULL,
  "Target" TEXT NOT NULL,
  "PluginName" TEXT NOT NULL,
  "PluginMethod" TEXT NOT NULL,
  "Plugin" JSON
);
CREATE TABLE "Input" (
  "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
  "ProjectID" TEXT NOT NULL REFERENCES "Project" ("ID"),
  "Content" TEXT NOT NULL,
  "Source" TEXT NOT NULL,
  "PluginName" TEXT NOT NULL,
  "PluginMethod" TEXT NOT NULL,
  "Plugin" JSON
);
CREATE TABLE "Analyzer" (
  "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
  "ProjectID" TEXT NOT NULL REFERENCES "Project" ("ID"),
  "Content" TEXT NOT NULL,
  "PluginName" TEXT NOT NULL,
  "PluginMethod" TEXT NOT NULL,
  "Plugin" JSON
);
CREATE INDEX "idx_translator__projectid" ON "Translator" ("ProjectID");
CREATE INDEX "idx_output__projectid" ON "Output" ("ProjectID");
CREATE INDEX "idx_input__projectid" ON "Input" ("ProjectID");
CREATE INDEX "idx_analyzer__projectid" ON "Analyzer" ("ProjectID");
COMMIT;
