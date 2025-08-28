//! Error handling for UFO/GLIF parsing and related I/O operations.
//!
//! This module defines the [`Error`] type, its associated [`ErrorKind`], and a
//! [`Result`] alias for convenience. It centralizes error construction and conversion
//! from common sources (I/O, XML, plist parsing, and numeric/string parsing).
//!
//! Key features:
//! - Structured error kinds for categorizing failure modes.
//! - Optional path and context fields for richer error messages.
//! - Automatic conversions (`From` impls) from standard and library errors.
//! - Compatible with the standard [`std::error::Error`] trait for use with `?`.

use std::error;
use std::fmt;
use std::io;
use std::num::{ParseFloatError, ParseIntError};
use std::str::Utf8Error;

/// A specialized [`Result`] type for operations that return [`Error`].
pub type Result<T> = std::result::Result<T, Error>;

/// Categories of errors that can occur while parsing UFO or GLIF data.
#[derive(Debug, PartialEq, Eq)]
pub enum ErrorKind {
    /// Underlying I/O error (file access, reading, etc.).
    Io,
    /// Failure while parsing a property list (`.plist`).
    Plist,
    /// Failure while parsing XML.
    Xml,
    /// Failure while parsing integers, floats, or UTF-8 strings.
    Parse,
    /// A requested file was not found.
    FileNotFound,
    /// An expected XML attribute was missing.
    MissingAttribute(String),
    /// Any other error not covered by the above kinds.
    Other(String),
}

impl fmt::Display for ErrorKind {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io => write!(f, "I/O error"),
            Self::Plist => write!(f, "Plist parsing error"),
            Self::Xml => write!(f, "Xml parsing error"),
            Self::Parse => write!(f, "Parsing error"),
            Self::FileNotFound => write!(f, "File not found"),
            Self::MissingAttribute(attr) => write!(f, "Missing attribute: {}", attr),
            Self::Other(msg) => write!(f, "{}", msg),
        }
    }
}

/// A structured error type for UFO/GLIF operations.
///
/// This type wraps an [`ErrorKind`] and may include:
/// - An optional file path (`path`) indicating where the error occurred.
/// - An optional context message (`context`) describing what was being done.
/// - An optional underlying cause (`cause`) implementing [`std::error::Error`].
#[derive(Debug)]
pub struct Error {
    kind: ErrorKind,
    path: Option<String>,
    context: Option<String>,
    cause: Option<Box<dyn error::Error + Send + Sync>>,
}

impl Error {
    /// Creates a new error with the given kind and no additional context.
    pub fn new(kind: ErrorKind) -> Self {
        Self {
            kind,
            path: None,
            context: None,
            cause: None,
        }
    }

    /// Adds a file path to the error for more detailed reporting.
    pub fn with_path(mut self, path: impl Into<String>) -> Self {
        self.path = Some(path.into());
        self
    }

    /// Adds a context message to the error, describing what was happening.
    pub fn with_context<C, F>(mut self, context: F) -> Self
    where
        C: fmt::Display + Send + Sync + 'static,
        F: FnOnce() -> C,
    {
        self.context = Some(context().to_string());
        self
    }

    /// Adds an underlying cause to the error.
    ///
    /// This is typically used when converting from another error type so that its details are
    /// preserved.
    pub fn with_cause(mut self, cause: impl error::Error + Send + Sync + 'static) -> Self {
        self.cause = Some(Box::new(cause));
        self
    }

    /// Returns the kind of this error.
    pub fn kind(&self) -> &ErrorKind {
        &self.kind
    }

    /// Returns the optional file path associated with this error.
    pub fn path(&self) -> &Option<String> {
        &self.path
    }

    /// Returns the optional context message associated with this error.
    pub fn context(&self) -> &Option<String> {
        &self.context
    }
}

impl fmt::Display for Error {
    /// Formats the error into a human-readable string, including
    /// context and file path if available.
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match (&self.context, &self.path) {
            (Some(ctx), Some(path)) => write!(f, "{} for '{}': {}", ctx, path, self.kind),
            (Some(ctx), None) => write!(f, "{}: {}", ctx, self.kind),
            (None, Some(path)) => write!(f, "An error occurred for '{}': {}", path, self.kind),
            (None, None) => write!(f, "{}", self.kind),
        }
    }
}

impl error::Error for Error {
    /// Returns the underlying cause, if one exists.
    fn source(&self) -> Option<&(dyn error::Error + 'static)> {
        // Cast the reference to &(dyn Error) (no Send + Sync) to satisfy error::Error
        self.cause
            .as_ref()
            .map(|e| e.as_ref() as &(dyn error::Error + 'static))
    }
}

impl From<io::Error> for Error {
    /// Converts an I/O error into [`Error`], mapping `NotFound` to [`ErrorKind::FileNotFound`].
    fn from(err: io::Error) -> Self {
        let kind = match err.kind() {
            io::ErrorKind::NotFound => ErrorKind::FileNotFound,
            _ => ErrorKind::Io,
        };
        Self::new(kind).with_cause(err)
    }
}

impl From<plist::Error> for Error {
    /// Converts a plist parsing error into [`ErrorKind::Plist`].
    fn from(err: plist::Error) -> Self {
        Self::new(ErrorKind::Plist).with_cause(err)
    }
}

impl From<quick_xml::Error> for Error {
    /// Converts an XML parsing error into [`ErrorKind::Xml`].
    fn from(err: quick_xml::Error) -> Self {
        Self::new(ErrorKind::Xml).with_cause(err)
    }
}

impl From<ParseIntError> for Error {
    /// Converts an integer parsing error into [`ErrorKind::Parse`].
    fn from(err: ParseIntError) -> Self {
        Self::new(ErrorKind::Parse).with_cause(err)
    }
}

impl From<ParseFloatError> for Error {
    /// Converts a floating-point parsing error into [`ErrorKind::Parse`].
    fn from(err: ParseFloatError) -> Self {
        Self::new(ErrorKind::Parse).with_cause(err)
    }
}

impl From<Utf8Error> for Error {
    /// Converts a UTF-8 decoding error into [`ErrorKind::Parse`].
    fn from(err: Utf8Error) -> Self {
        Self::new(ErrorKind::Parse).with_cause(err)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::error::Error as StdError;
    use std::io;
    use std::num::{ParseFloatError, ParseIntError};
    use std::str::Utf8Error;

    fn make_parse_int_error() -> ParseIntError {
        "not_an_int".parse::<i32>().unwrap_err()
    }

    fn make_parse_float_error() -> ParseFloatError {
        "not_a_float".parse::<f32>().unwrap_err()
    }

    fn make_utf8_error() -> Utf8Error {
        let bytes = vec![0xff];
        std::str::from_utf8(&bytes).unwrap_err()
    }

    #[test]
    fn errorkind_display_variants() {
        assert_eq!(ErrorKind::Io.to_string(), "I/O error");
        assert_eq!(ErrorKind::Plist.to_string(), "Plist parsing error");
        assert_eq!(ErrorKind::Xml.to_string(), "Xml parsing error");
        assert_eq!(ErrorKind::Parse.to_string(), "Parsing error");
        assert_eq!(ErrorKind::FileNotFound.to_string(), "File not found");
        assert_eq!(
            ErrorKind::MissingAttribute("attr".into()).to_string(),
            "Missing attribute: attr"
        );
        assert_eq!(
            ErrorKind::Other("something bad".into()).to_string(),
            "something bad"
        );
    }

    #[test]
    fn error_builders_and_getters() {
        let err = Error::new(ErrorKind::Io)
            .with_path("some/file.ufo")
            .with_context(|| "reading file");
        assert_eq!(err.kind(), &ErrorKind::Io);
        assert_eq!(err.path(), &Some("some/file.ufo".into()));
        assert_eq!(err.context(), &Some("reading file".into()));
    }

    #[test]
    fn error_display_variations() {
        let base = Error::new(ErrorKind::Parse);
        assert_eq!(base.to_string(), "Parsing error");

        let with_path = Error::new(ErrorKind::Parse).with_path("file.glif");
        assert_eq!(
            with_path.to_string(),
            "An error occurred for 'file.glif': Parsing error"
        );

        let with_context = Error::new(ErrorKind::Parse).with_context(|| "while parsing");
        assert_eq!(with_context.to_string(), "while parsing: Parsing error");

        let with_both = Error::new(ErrorKind::Parse)
            .with_path("file.glif")
            .with_context(|| "while parsing");
        assert_eq!(
            with_both.to_string(),
            "while parsing for 'file.glif': Parsing error"
        );
    }

    #[test]
    fn error_source_returns_cause() {
        let io_err = io::Error::new(io::ErrorKind::Other, "disk failed");
        let err = Error::new(ErrorKind::Io).with_cause(io_err);
        let src = err.source().unwrap();
        assert_eq!(src.to_string(), "disk failed");
    }

    #[test]
    fn from_io_error_other() {
        let io_err = io::Error::new(io::ErrorKind::Other, "oh no");
        let err: Error = io_err.into();
        assert_eq!(err.kind(), &ErrorKind::Io);
        assert!(err.source().is_some());
    }

    #[test]
    fn from_io_error_not_found() {
        let io_err = io::Error::new(io::ErrorKind::NotFound, "missing");
        let err: Error = io_err.into();
        assert_eq!(err.kind(), &ErrorKind::FileNotFound);
        assert!(err.source().is_some());
    }

    #[test]
    fn from_plist_error() {
        let data = b"ivalid plist";
        let result: std::result::Result<plist::Value, plist::Error> = plist::from_bytes(data);
        let plist_err = result.unwrap_err();
        let err: Error = plist_err.into();
        assert_eq!(err.kind(), &ErrorKind::Plist);
        assert!(err.source().is_some());
    }

    #[test]
    fn from_quick_xml_error() {
        let data = "<invalid xml";
        let mut reader = quick_xml::Reader::from_str(data);
        let xml_err = reader.read_event().unwrap_err();
        let err: Error = xml_err.into();
        assert_eq!(err.kind(), &ErrorKind::Xml);
        assert!(err.source().is_some());
    }

    #[test]
    fn from_parse_int_error() {
        let int_err = make_parse_int_error();
        let err: Error = int_err.into();
        assert_eq!(err.kind(), &ErrorKind::Parse);
        assert!(err.source().is_some());
    }

    #[test]
    fn from_parse_float_error() {
        let float_err = make_parse_float_error();
        let err: Error = float_err.into();
        assert_eq!(err.kind(), &ErrorKind::Parse);
        assert!(err.source().is_some());
    }

    #[test]
    fn from_utf8_error() {
        let utf8_err = make_utf8_error();
        let err: Error = utf8_err.into();
        assert_eq!(err.kind(), &ErrorKind::Parse);
        assert!(err.source().is_some());
    }
}
