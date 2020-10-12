import React, { useState } from "react";
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';

export default function HTMLEditor(props) {
  return (
    <ReactQuill theme="snow"
                value={props.value}
                onChange={value => {
                  if (value.replace(/<(.|\n)*?>/g, '').trim().length === 0) {
                    props.onChange('');
                  } else {
                    props.onChange(value);
                  }
                }}
    />
  );
}
