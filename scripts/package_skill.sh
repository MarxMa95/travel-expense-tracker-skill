#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_SRC="$ROOT_DIR/skill"
DIST_DIR="$ROOT_DIR/dist"
TMP_DIR="$DIST_DIR/tmp"
PACKAGE_NAME="travel-expense-tracker.skill"
TOP_DIR="travel-expense-tracker"

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR/$TOP_DIR" "$DIST_DIR"

cp -R "$SKILL_SRC"/* "$TMP_DIR/$TOP_DIR/"

(
  cd "$TMP_DIR"
  rm -f "$DIST_DIR/$PACKAGE_NAME"
  zip -qr "$DIST_DIR/$PACKAGE_NAME" "$TOP_DIR"
)

rm -rf "$TMP_DIR"
echo "Created $DIST_DIR/$PACKAGE_NAME"
